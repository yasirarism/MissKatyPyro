from functools import partial, wraps
from time import time
from traceback import format_exc as err
from typing import Optional, Union

from pyrogram import Client, enums
from pyrogram.errors import ChannelPrivate, ChatAdminRequired, ChatWriteForbidden
from pyrogram.types import CallbackQuery, Message

from misskaty import app
from misskaty.helper.sqlite_helper import Cache
from misskaty.vars import SUDO

from ...helper.localization import (
    default_language,
    get_lang,
    get_locale_string,
    langdict,
)


async def member_permissions(chat_id: int, user_id: int, client):
    perms = []
    try:
        member = (await client.get_chat_member(chat_id, user_id)).privileges
        if member.can_post_messages:
            perms.append("can_post_messages")
        if member.can_edit_messages:
            perms.append("can_edit_messages")
        if member.can_delete_messages:
            perms.append("can_delete_messages")
        if member.can_restrict_members:
            perms.append("can_restrict_members")
        if member.can_promote_members:
            perms.append("can_promote_members")
        if member.can_change_info:
            perms.append("can_change_info")
        if member.can_invite_users:
            perms.append("can_invite_users")
        if member.can_pin_messages:
            perms.append("can_pin_messages")
        if member.can_manage_video_chats:
            perms.append("can_manage_video_chats")
        return perms
    except:
        return []


async def check_perms(
    message: Union[CallbackQuery, Message],
    permissions: Optional[Union[list, str]],
    complain_missing_perms: bool,
    strings,
) -> bool:
    if isinstance(message, CallbackQuery):
        sender = partial(message.answer, show_alert=True)
        chat = message.message.chat
    else:
        sender = message.reply_text
        chat = message.chat
    if not message.from_user:
        return bool(message.sender_chat and message.sender_chat.id == message.chat.id)
    try:
        user = await chat.get_member(message.from_user.id)
    except ChatAdminRequired:
        return False
    if user.status == enums.ChatMemberStatus.OWNER:
        return True

    # No permissions specified, accept being an admin.
    if not permissions and user.status == enums.ChatMemberStatus.ADMINISTRATOR:
        return True
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR:
        if complain_missing_perms:
            await sender(strings("no_admin_error"))
        return False

    if isinstance(permissions, str):
        permissions = [permissions]

    missing_perms = [
        permission
        for permission in permissions
        if not getattr(user.privileges, permission)
    ]

    if not missing_perms:
        return True
    if complain_missing_perms:
        await sender(
            strings("no_permission_error").format(permissions=", ".join(missing_perms))
        )
    return False


admins_in_chat = Cache(filename="admin_cache.db", path="cache", in_memory=False)


async def list_admins(chat_id: int):
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    try:
        admins_in_chat.add(
            chat_id,
            {
                "last_updated_at": time(),
                "data": [
                    member.user.id
                    async for member in app.get_chat_members(
                        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
                    )
                ],
            },
            timeout=6 * 60 * 60,
        )
        return admins_in_chat[chat_id]["data"]
    except ChannelPrivate:
        return


async def authorised(func, subFunc2, client, message, *args, **kwargs):
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await message.chat.leave()
    except Exception as e:
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(e)
    return subFunc2


async def unauthorised(message: Message, permission, subFunc2):
    text = f"You don't have the required permission to perform this action.\n**Permission:** __{permission}__"
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await message.chat.leave()
    return subFunc2


def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if message.sender_chat and message.sender_chat.id == message.chat.id:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(message, permission, subFunc2)
            # For admins and sudo users
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID, client)
            if userID not in SUDO and permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(func, subFunc2, client, message, *args, **kwargs)

        return subFunc2

    return subFunc


def require_admin(
    permissions: Union[list, str] = None,
    allow_in_private: bool = False,
    complain_missing_perms: bool = True,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            client: Client, message: Union[CallbackQuery, Message], *args, **kwargs
        ):
            lang = await get_lang(message)
            strings = partial(
                get_locale_string,
                langdict[lang].get("admin", langdict[default_language]["admin"]),
                lang,
                "admin",
            )

            if isinstance(message, CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
            elif isinstance(message, Message):
                sender = message.reply_text
                msg = message
            else:
                raise NotImplementedError(
                    f"require_admin can't process updates with the type '{message.__name__}' yet."
                )

            # We don't actually check private and channel chats.
            if msg.chat.type == enums.ChatType.PRIVATE:
                if allow_in_private:
                    return await func(client, message, *args, *kwargs)
                return await sender(strings("private_not_allowed"))
            if msg.chat.type == enums.ChatType.CHANNEL:
                return await func(client, message, *args, *kwargs)
            has_perms = await check_perms(
                message, permissions, complain_missing_perms, strings
            )
            if has_perms:
                return await func(client, message, *args, *kwargs)

        return wrapper

    return decorator
