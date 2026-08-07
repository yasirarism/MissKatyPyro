"""
MIT License

Copyright (c) 2023 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import contextlib
import os
import re
from logging import getLogger
from time import time

from pyrogram import Client, enums, filters
from pyrogram import types as pyro_types
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    PeerIdInvalid,
    UsernameNotOccupied,
)
from pyrogram.types import ChatMember, ChatPrivileges, Message

from database.warn_db import add_warn, get_warn, remove_warns
from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.permissions import (
    admins_in_chat,
    list_admins,
    member_permissions,
)
from misskaty.core.keyboard import ikb
from misskaty.helper.functions import (
    extract_user,
    extract_user_and_reason,
    int_to_alpha,
    time_converter,
)
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.chat_permissions import empty_chat_permissions
from misskaty.vars import COMMAND_HANDLER, SUDO, OWNER_ID

LOGGER = getLogger("MissKaty")

__MODULE__ = "Admin"
__HELP__ = """
/ban - Ban A User From A Group
/dban - Delete the replied message banning its sender
/tban - Ban A User For Specific Time
/unban - Unban A User
/listban - Ban a user from groups listed in a message
/listunban - Unban a user from groups listed in a message
/warn - Warn A User
/dwarn - Delete the replied message warning its sender
/rmwarns - Remove All Warning of A User
/warns - Show Warning Of A User
/kick - Kick A User
/dkick - Delete the replied message kicking its sender
/purge - Purge Messages
/purge [n] - Purge "n" number of messages from replied message
/del - Delete Replied Message
/promote - Promote A Member
/fullpromote - Promote A Member With All Rights
/demote - Demote A Member
/pin - Pin A Message
/mute - Mute A User
/tmute - Mute A User For Specific Time
/unmute - Unmute A User
/ban_ghosts - Ban Deleted Accounts
/report | @admins | @admin - Report A Message To Admins.
/set_chat_title - Change The Name Of A Group/Channel.
/set_chat_photo - Change The PFP Of A Group/Channel.
/set_user_title - Change The Administrator Title Of An Admin.
/mentionall - Mention all members in a groups.
"""


class AdminHelper:
    """Shared helpers for admin actions."""

    @staticmethod
    def is_self(client: Client, user_id: int) -> bool:
        return user_id == client.me.id

    @staticmethod
    def is_sudo_or_owner(user_id: int) -> bool:
        return user_id in SUDO or user_id == OWNER_ID

    @staticmethod
    async def is_admin(chat_id: int, user_id: int) -> bool:
        return user_id in await list_admins(chat_id)

    @staticmethod
    async def safe_api(coro, *, on_not_admin: str | None = None):
        try:
            return await coro, None
        except ChatAdminRequired:
            return None, on_not_admin or "Please give me proper admin permissions."
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await coro, None
        except Exception as exc:
            return None, str(exc)

    @staticmethod
    async def ensure_restrict_permission(chat_id: int, client: Client, strings) -> bool:
        perms = await member_permissions(chat_id, client.me.id)
        if "can_restrict_members" not in perms:
            await strings("no_ban_permission")
            return False
        return True


# Admin cache reload
@app.on_chat_member_updated(filters.group, group=5)
async def admin_cache_func(_, cmu):
    if cmu.old_chat_member and cmu.old_chat_member.promoted_by:
        try:
            admins_in_chat[cmu.chat.id] = {
                "last_updated_at": time(),
                "data": [
                    member.user.id
                    async for member in app.get_chat_members(
                        cmu.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
                    )
                ],
            }
            LOGGER.info(f"Updated admin cache for {cmu.chat.id} [{cmu.chat.title}]")
        except Exception:
            pass


# Purge CMD
@app.on_cmd("purge")
@app.adminsOnly("can_delete_messages")
@use_chat_lang()
async def purge(_, ctx: Message, strings):
    try:
        repliedmsg = ctx.reply_to_message
        await ctx.delete()

        if not repliedmsg:
            return await ctx.reply(strings("purge_no_reply"))

        cmd = ctx.command
        if len(cmd) > 1 and cmd[1].isdigit():
            purge_to = repliedmsg.id + int(cmd[1])
            purge_to = min(purge_to, ctx.id)
        else:
            purge_to = ctx.id

        chat_id = ctx.chat.id
        message_ids = []
        del_total = 0

        for message_id in range(repliedmsg.id, purge_to):
            message_ids.append(message_id)
            if len(message_ids) == 100:
                _, err = await AdminHelper.safe_api(
                    app.delete_messages(chat_id=chat_id, message_ids=message_ids, revoke=True)
                )
                if err:
                    return await ctx.reply(f"ERROR: {err}")
                del_total += len(message_ids)
                message_ids = []

        if message_ids:
            _, err = await AdminHelper.safe_api(
                app.delete_messages(chat_id=chat_id, message_ids=message_ids, revoke=True)
            )
            if err:
                return await ctx.reply(f"ERROR: {err}")
            del_total += len(message_ids)

        await ctx.reply(strings("purge_success").format(del_total=del_total))
    except Exception as err:
        await ctx.reply(f"ERROR: {err}")


# Kick members
@app.on_cmd(["kick", "dkick"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def kickFunc(client: Client, ctx: Message, strings) -> Message:
    if ctx.reply_to_message and ctx.reply_to_message.sender_chat:
        return await ctx.reply(strings("user_not_found"))
    user_id, reason = await extract_user_and_reason(ctx)
    if not user_id:
        return await ctx.reply(strings("user_not_found"))
    if AdminHelper.is_self(client, user_id):
        return await ctx.reply(strings("kick_self_err"))
    if AdminHelper.is_sudo_or_owner(user_id):
        return await ctx.reply(strings("kick_sudo_err"))
    if await AdminHelper.is_admin(ctx.chat.id, user_id):
        return await ctx.reply(strings("kick_admin_err"))

    try:
        user = await app.get_users(user_id)
    except PeerIdInvalid:
        return await ctx.reply(strings("user_not_found"))

    msg = strings("kick_msg").format(
        mention=user.mention,
        id=user.id,
        kicker=ctx.from_user.mention if ctx.from_user else "Anon Admin",
        reasonmsg=reason or "-",
    )
    if ctx.command[0][0] == "d":
        if ctx.reply_to_message:
            await ctx.reply_to_message.delete()
    if not await AdminHelper.ensure_restrict_permission(ctx.chat.id, client, strings):
        return
    _, err = await AdminHelper.safe_api(ctx.chat.ban_member(user_id), on_not_admin=strings("no_ban_permission"))
    if err:
        return await ctx.reply(err)
    await ctx.reply(msg)
    await asyncio.sleep(1)
    _, err = await AdminHelper.safe_api(ctx.chat.unban_member(user_id))
    if err:
        LOGGER.warning(f"Unban after kick failed: {err}")


# Ban/DBan/TBan User
@app.on_cmd(["ban", "dban", "tban"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def banFunc(client, message, strings):
    try:
        user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    except UsernameNotOccupied:
        return await message.reply("Sorry, i didn't know that user.")

    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if AdminHelper.is_self(client, user_id):
        return await message.reply_text(strings("ban_self_err"))
    if AdminHelper.is_sudo_or_owner(user_id):
        return await message.reply_text(strings("ban_sudo_err"))
    if await AdminHelper.is_admin(message.chat.id, user_id):
        return await message.reply_text(strings("ban_admin_err"))

    # Mention: channel/sender-chat pakai judulnya, user biasa pakai mention
    reply = message.reply_to_message
    if reply and reply.sender_chat and reply.sender_chat.id == user_id:
        mention = reply.sender_chat.title or "Anon"
    else:
        try:
            mention = (await app.get_users(user_id)).mention
        except PeerIdInvalid:
            return await message.reply_text(strings("user_not_found"))

    msg = strings("ban_msg").format(
        mention=mention,
        id=user_id,
        banner=message.from_user.mention if message.from_user else "Anon",
    )
    if message.command[0][0] == "d" and message.reply_to_message:
        await message.reply_to_message.delete()
    if message.command[0] == "tban":
        if not reason:
            return await message.reply(strings("incorrect_time"))
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        try:
            temp_ban = await time_converter(time_value)
        except ValueError:
            return await message.reply(strings("incorrect_time"))
        msg += strings("banner_time").format(val=time_value)
        if temp_reason:
            msg += strings("banned_reason").format(reas=temp_reason)
        if len(time_value[:-1]) >= 3:
            return await message.reply_text(strings("no_more_99"))
        _, err = await AdminHelper.safe_api(
            message.chat.ban_member(user_id, until_date=temp_ban),
            on_not_admin=strings("no_ban_permission"),
        )
        if err:
            return await message.reply(err)
        return await message.reply_text(msg)
    if reason:
        msg += strings("banned_reason").format(reas=reason)
    keyboard = ikb({"🚨 Unban 🚨": f"unban_{user_id}"})
    _, err = await AdminHelper.safe_api(message.chat.ban_member(user_id), on_not_admin=strings("no_ban_permission"))
    if err:
        return await message.reply(err)
    await message.reply(msg, reply_markup=keyboard)


# Unban members
@app.on_cmd("unban", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def unban_func(_, message, strings):
    reply = message.reply_to_message

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text(strings("unban_channel_err"))

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = reply.from_user.id
    else:
        return await message.reply(strings("give_unban_user"))
    _, err = await AdminHelper.safe_api(message.chat.unban_member(user), on_not_admin=strings("no_ban_permission"))
    if err:
        return await message.reply(err)
    try:
        umention = (await app.get_users(user)).mention
    except (PeerIdInvalid, IndexError):
        umention = f"<code>{user}</code>"
    await message.reply(strings("unban_success").format(umention=umention))


# Ban users listed in a message
@app.on_message(
    (filters.user(SUDO) | filters.user(OWNER_ID)) & filters.command("listban", COMMAND_HANDLER) & filters.group
)
@use_chat_lang()
async def list_ban_(c, message, strings):
    userid, msglink_reason = await extract_user_and_reason(message)
    if not userid or not msglink_reason:
        return await message.reply_text(strings("give_idban_with_msg_link"))
    if len(msglink_reason.split(" ")) == 1:
        return await message.reply_text(strings("give_reason_list_ban"))
    lreason = msglink_reason.split()
    messagelink, reason = lreason[0], " ".join(lreason[1:])
    if not re.search(r"(https?://)?t(telegram)?\.me/\w+/\d+", messagelink):
        return await message.reply_text(strings("invalid_tg_link"))
    if AdminHelper.is_self(c, userid):
        return await message.reply_text(strings("ban_self_err"))
    if AdminHelper.is_sudo_or_owner(userid):
        return await message.reply_text(strings("ban_sudo_err"))
    splitted = messagelink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(strings("multiple_ban_progress"))
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\w+", msgtext)
    except Exception:
        return await m.edit_text(strings("failed_get_uname"))
    count = 0
    for username in gusernames:
        try:
            await app.ban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention
    msg = strings("listban_msg").format(
        mention=mention, uid=userid, frus=message.from_user.mention, ct=count, reas=reason
    )
    await m.edit_text(msg)


# Unban users listed in a message
@app.on_message(
    (filters.user(SUDO) | filters.user(OWNER_ID)) & filters.command("listunban", COMMAND_HANDLER) & filters.group
)
@use_chat_lang()
async def list_unban(_, message, strings):
    userid, msglink = await extract_user_and_reason(message)
    if not userid or not msglink:
        return await message.reply_text(strings("give_idunban_with_msg_link"))
    if not re.search(r"(https?://)?t(telegram)?\.me/\w+/\d+", msglink):
        return await message.reply_text(strings("invalid_tg_link"))
    splitted = msglink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(strings("multiple_unban_progress"))
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\w+", msgtext)
    except Exception:
        return await m.edit_text(strings("failed_get_uname"))
    count = 0
    for username in gusernames:
        try:
            await app.unban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention
    msg = strings("listunban_msg").format(
        mention=mention, uid=userid, frus=message.from_user.mention, ct=count
    )
    await m.edit_text(msg)


# Delete messages
@app.on_cmd("del", group_only=True)
@app.adminsOnly("can_delete_messages")
@use_chat_lang()
async def deleteFunc(_, message, strings):
    if not message.reply_to_message:
        return await message.reply_text(strings("delete_no_reply"))
    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception:
        await message.reply(strings("no_delete_perm"))


# Promote Members
@app.on_cmd(["promote", "fullpromote"], self_admin=True, group_only=True)
@app.adminsOnly("can_promote_members")
@use_chat_lang()
async def promoteFunc(client, message, strings):
    if message.reply_to_message and message.reply_to_message.sender_chat:
        return await message.reply(strings("user_not_found"))
    try:
        user_id = await extract_user(message)
        umention = (await client.get_users(user_id)).mention
    except Exception:
        return await message.reply(strings("invalid_id_uname"))
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if AdminHelper.is_self(client, user_id):
        return await message.reply(strings("promote_self_err"))
    if not bot:
        return await message.reply("I'm not an admin in this chat.")
    if not bot.can_promote_members:
        return await message.reply(strings("no_promote_perm"))
    try:
        if message.command[0][0] == "f":
            await message.chat.promote_member(
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_change_info=bot.can_change_info,
                    can_invite_users=bot.can_invite_users,
                    can_delete_messages=bot.can_delete_messages,
                    can_restrict_members=bot.can_restrict_members,
                    can_pin_messages=bot.can_pin_messages,
                    can_promote_members=bot.can_promote_members,
                    can_manage_chat=bot.can_manage_chat,
                    can_manage_video_chats=bot.can_manage_video_chats,
                ),
            )
            return await message.reply_text(
                strings("full_promote").format(umention=umention)
            )

        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=False,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
        await message.reply(strings("normal_promote").format(umention=umention))
    except Exception as err:
        await message.reply(err)


# Demote Member
@app.on_cmd("demote", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def demote(client, message, strings):
    try:
        user_id = await extract_user(message)
    except Exception:
        return await message.reply(strings("invalid_id_uname"))
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if AdminHelper.is_self(client, user_id):
        return await message.reply_text(strings("demote_self_err"))
    if AdminHelper.is_sudo_or_owner(user_id):
        return await message.reply_text(strings("demote_sudo_err"))
    if not await AdminHelper.is_admin(message.chat.id, user_id):
        return await message.reply_text(strings("demote_not_admin"))
    _, err = await AdminHelper.safe_api(
        message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_invite_users=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_chat=False,
                can_manage_video_chats=False,
            ),
        ),
        on_not_admin=strings("no_demote_perm"),
    )
    if err:
        return await message.reply(err)
    try:
        umention = (await app.get_users(user_id)).mention
    except (PeerIdInvalid, IndexError):
        umention = f"<code>{user_id}</code>"
    await message.reply_text(strings("demote_success").format(umention=umention))


# Pin Messages
@app.on_cmd(["pin", "unpin"])
@app.adminsOnly("can_pin_messages")
@use_chat_lang()
async def pin(_, message, strings):
    if not message.reply_to_message:
        return await message.reply_text(strings("pin_no_reply"))
    r = message.reply_to_message
    try:
        if message.command[0][0] == "u":
            await r.unpin()
            return await message.reply_text(
                strings("unpin_success").format(link=r.link),
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
            )
        await r.pin(disable_notification=True)
        await message.reply(
            strings("pin_success").format(link=r.link),
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )
    except ChatAdminRequired:
        await message.reply(
            strings("pin_no_perm"),
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        )
    except Exception as e:
        await message.reply(str(e))


# Mute members
@app.on_cmd(["mute", "tmute"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def mute(client, message, strings):
    try:
        user_id, reason = await extract_user_and_reason(message)
    except Exception as err:
        return await message.reply(f"ERROR: {err}")
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if AdminHelper.is_self(client, user_id):
        return await message.reply_text(strings("mute_self_err"))
    if AdminHelper.is_sudo_or_owner(user_id):
        return await message.reply_text(strings("mute_sudo_err"))
    if await AdminHelper.is_admin(message.chat.id, user_id):
        return await message.reply_text(strings("mute_admin_err"))

    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨 Unmute 🚨": f"unmute_{user_id}"})
    msg = strings("mute_msg").format(
        mention=mention,
        muter=message.from_user.mention if message.from_user else "Anon",
    )
    if message.command[0] == "tmute":
        if not reason:
            return await message.reply(strings("incorrect_time"))
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        try:
            temp_mute = await time_converter(time_value)
        except ValueError:
            return await message.reply(strings("incorrect_time"))
        msg += strings("muted_time").format(val=time_value)
        if temp_reason:
            msg += strings("banned_reason").format(reas=temp_reason)
        if len(time_value[:-1]) >= 3:
            return await message.reply_text(strings("no_more_99"))
        _, err = await AdminHelper.safe_api(
            message.chat.restrict_member(
                user_id,
                permissions=empty_chat_permissions(),
                until_date=temp_mute,
            ),
            on_not_admin=strings("no_ban_permission"),
        )
        if err:
            return await message.reply(err)
        return await message.reply_text(msg, reply_markup=keyboard)
    if reason:
        msg += strings("banned_reason").format(reas=reason)
    _, err = await AdminHelper.safe_api(
        message.chat.restrict_member(user_id, permissions=empty_chat_permissions()),
        on_not_admin=strings("no_ban_permission"),
    )
    if err:
        return await message.reply(err)
    await message.reply_text(msg, reply_markup=keyboard)


# Unmute members
@app.on_cmd("unmute", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def unmute(_, message, strings):
    try:
        user_id = await extract_user(message)
    except Exception:
        return await message.reply(strings("invalid_id_uname"))
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    _, err = await AdminHelper.safe_api(message.chat.unban_member(user_id))
    if err:
        return await message.reply(err)
    try:
        umention = (await app.get_users(user_id)).mention
    except (PeerIdInvalid, IndexError):
        umention = f"<code>{user_id}</code>"
    await message.reply(strings("unmute_msg").format(umention=umention))


@app.on_cmd(["warn", "dwarn"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def warn_user(client, message, strings):
    try:
        user_id, reason = await extract_user_and_reason(message)
    except UsernameNotOccupied:
        return await message.reply("Sorry, i didn't know that user.")
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if AdminHelper.is_self(client, user_id):
        return await message.reply_text(strings("warn_self_err"))
    if AdminHelper.is_sudo_or_owner(user_id):
        return await message.reply_text(strings("warn_sudo_err"))
    if await AdminHelper.is_admin(chat_id, user_id):
        return await message.reply_text(strings("warn_admin_err"))

    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({strings("rm_warn_btn"): f"unwarn_{user_id}"})
    warns = warns["warns"] if warns else 0
    if message.command[0][0] == "d" and message.reply_to_message:
        await message.reply_to_message.delete()
    if warns >= 2:
        _, err = await AdminHelper.safe_api(message.chat.ban_member(user_id))
        if err:
            return await message.reply(err)
        await message.reply(strings("exceed_warn_msg").format(mention=mention))
        await remove_warns(chat_id, await int_to_alpha(user_id))
        return
    warn = {"warns": warns + 1}
    msg = strings("warn_msg").format(
        mention=mention,
        warner=message.from_user.mention if message.from_user else "Anon",
        reas=reason or "No Reason Provided.",
        twarn=warns + 1,
    )
    await message.reply(msg, reply_markup=keyboard)
    await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_"))
@use_chat_lang()
async def remove_warning(_, cq, strings):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    if "can_restrict_members" not in permissions:
        return await cq.answer(
            strings("no_permission_error").format(permissions=permissions),
            show_alert=True,
        )
    user_id = int(cq.data.split("_")[1])
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    warns = warns["warns"] if warns else 0
    if not warns or warns == 0:
        return await cq.answer(
            strings("user_no_warn").format(
                mention=(
                    cq.message.reply_to_message.from_user.mention
                    if cq.message.reply_to_message and cq.message.reply_to_message.from_user
                    else f"<code>{user_id}</code>"
                )
            )
        )
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = (cq.message.text.markdown or "") if cq.message.text else ""
    text = f"~~{text}~~\n\n"
    text += strings("unwarn_msg").format(mention=from_user.mention)
    await cq.message.edit(text)


@app.on_callback_query(filters.regex("unmute_"))
@use_chat_lang()
async def unmute_user(_, cq, strings):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    if "can_restrict_members" not in permissions:
        return await cq.answer(
            strings("no_permission_error").format(permissions=permissions),
            show_alert=True,
        )
    user_id = int(cq.data.split("_")[1])
    text = (cq.message.text.markdown or "") if cq.message.text else ""
    text = f"~~{text}~~\n\n"
    text += strings("rmmute_msg").format(mention=from_user.mention)
    _, err = await AdminHelper.safe_api(cq.message.chat.unban_member(user_id))
    if err:
        return await cq.answer(str(err))
    await cq.message.edit(text)


@app.on_callback_query(filters.regex("unban_"))
@use_chat_lang()
async def unban_user(_, cq, strings):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    if "can_restrict_members" not in permissions:
        return await cq.answer(
            strings("no_permission_error").format(permissions=permissions),
            show_alert=True,
        )
    user_id = int(cq.data.split("_")[1])
    text = (cq.message.text.markdown or "") if cq.message.text else ""
    text = f"~~{text}~~\n\n"
    text += strings("unban_msg").format(mention=from_user.mention)
    _, err = await AdminHelper.safe_api(cq.message.chat.unban_member(user_id))
    if err:
        return await cq.answer(str(err))
    await cq.message.edit(text)


# Remove Warn
@app.on_cmd("rmwarn", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def remove_warnings(_, message, strings):
    if not message.reply_to_message:
        return await message.reply_text(strings("reply_to_rm_warn"))
    if not message.reply_to_message.from_user:
        return await message.reply_text(strings("user_not_found"))
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    warns = warns["warns"] if warns else 0
    if warns == 0 or not warns:
        await message.reply_text(strings("user_no_warn").format(mention=mention))
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(strings("rmwarn_msg").format(mention=mention))


# Warns
@app.on_cmd("warns", group_only=True)
@use_chat_lang()
async def check_warns(_, message, strings):
    if not message.from_user:
        return
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    warns = warns["warns"] if warns else 0
    if not warns:
        return await message.reply_text(strings("user_no_warn").format(mention=mention))
    return await message.reply_text(
        strings("ch_warn_msg").format(mention=mention, warns=warns)
    )


# Report User in Group
@app.on_message(
    (
        filters.command("report", COMMAND_HANDLER)
        | filters.command(["admins", "admin"], prefixes="@")
    )
    & filters.group
)
@capture_err
@use_chat_lang()
async def report_user(_, ctx: Message, strings) -> Message:
    if len(ctx.text.split()) <= 1 and not ctx.reply_to_message:
        return await ctx.reply(strings("report_no_reply"))
    reply = ctx.reply_to_message if ctx.reply_to_message else ctx
    if reply.from_user:
        reply_id = reply.from_user.id
        user_mention = reply.from_user.mention
    elif reply.sender_chat:
        reply_id = reply.sender_chat.id
        user_mention = reply.sender_chat.title or "Anon"
    else:
        return await ctx.reply(strings("report_no_reply"))
    user_id = ctx.from_user.id if ctx.from_user else ctx.sender_chat.id
    if reply_id == user_id:
        return await ctx.reply(strings("report_self_err"))

    list_of_admins = await list_admins(ctx.chat.id)
    linked_chat = (await app.get_chat(ctx.chat.id)).linked_chat
    if linked_chat is None:
        if reply_id in list_of_admins or reply_id == ctx.chat.id:
            return await ctx.reply(strings("reported_is_admin"))
    elif (
        reply_id in list_of_admins
        or reply_id == ctx.chat.id
        or reply_id == linked_chat.id
    ):
        return await ctx.reply(strings("reported_is_admin"))
    text = strings("report_msg").format(user_mention=user_mention)
    admin_data = [
        m
        async for m in app.get_chat_members(
            ctx.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        )
    ]
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            continue
        text += f"<a href='tg://user?id={admin.user.id}'>\u2063</a>"
    await reply.reply(text)


@app.on_cmd("set_chat_title", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
@use_chat_lang()
async def set_chat_title(_, ctx: Message, strings):
    if len(ctx.command) < 2:
        return await ctx.reply_text(f"**Usage:**\n/{ctx.command[0]} NEW NAME")
    old_title = ctx.chat.title
    new_title = ctx.text.split(None, 1)[1]
    _, err = await AdminHelper.safe_api(ctx.chat.set_title(new_title))
    if err:
        return await ctx.reply(err)
    await ctx.reply_text(
        strings("chat_title_changed").format(old=old_title, new=new_title)
    )


@app.on_cmd("set_user_title", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
@use_chat_lang()
async def set_user_title(_, ctx: Message, strings):
    if not ctx.reply_to_message:
        return await ctx.reply_text("Reply to user's message to set his admin title")
    if not ctx.reply_to_message.from_user:
        return await ctx.reply_text("I can't change admin title of an unknown entity")
    if len(ctx.command) < 2:
        return await ctx.reply_text(
            "**Usage:**\n/set_user_title NEW ADMINISTRATOR TITLE"
        )
    title = ctx.text.split(None, 1)[1]
    from_user = ctx.reply_to_message.from_user
    _, err = await AdminHelper.safe_api(app.set_administrator_title(ctx.chat.id, from_user.id, title))
    if err:
        return await ctx.reply(err)
    await ctx.reply_text(
        strings("user_title_changed").format(mention=from_user.mention, title=title)
    )


@app.on_cmd("set_chat_photo", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
@use_chat_lang()
async def set_chat_photo(_, ctx: Message, strings):
    reply = ctx.reply_to_message

    if not reply:
        return await ctx.reply_text("Reply to a photo to set it as chat_photo")

    file = reply.document or reply.photo
    if not file:
        return await ctx.reply_text(
            "Reply to a photo or document to set it as chat_photo"
        )

    if file.file_size > 5000000:
        return await ctx.reply("File size too large.")

    photo = await reply.download()
    _, err = await AdminHelper.safe_api(ctx.chat.set_photo(photo=photo))
    try:
        if err:
            return await ctx.reply(f"Failed changed group photo. ERROR: {err}")
        await ctx.reply_text(strings("chat_photo_changed"))
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(photo)


@app.on_message(filters.group & filters.command("mentionall", COMMAND_HANDLER))
async def mentionall(client: Client, msg: Message):
    if not msg.from_user:
        return
    member = await msg.chat.get_member(msg.from_user.id)
    if member.status not in (
        enums.ChatMemberStatus.OWNER,
        enums.ChatMemberStatus.ADMINISTRATOR,
    ):
        return await client.send_message(
            msg.chat.id,
            "Admins only can do that !",
            reply_parameters=pyro_types.ReplyParameters(message_id=msg.id),
        )
    total = []
    async for m in client.get_chat_members(msg.chat.id):
        if not m.user or m.user.is_deleted:
            continue
        total.append(f"@{m.user.username}" if m.user.username else m.user.mention())

    if not total:
        return await msg.reply("No mentionable members found.")

    NUM = 4
    for i in range(0, len(total), NUM):
        text = "\n".join(total[i : i + NUM])
        try:
            await client.send_message(
                msg.chat.id,
                text,
                message_thread_id=msg.message_thread_id,
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as err:
            LOGGER.warning(f"mentionall chunk failed: {err}")
