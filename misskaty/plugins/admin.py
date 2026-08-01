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


class AdminManager:
    def __init__(
        self,
        client: Client,
        message: Message | None = None,
        callback=None,
        strings=None,
    ) -> None:
        self.client = client
        self.message = message
        self.callback = callback
        self.strings = strings
        self.chat = getattr(message, "chat", None) or getattr(callback, "message", None).chat
        self.from_user = getattr(message, "from_user", None) or getattr(callback, "from_user", None)

    # ---------- helpers ----------
    async def _reply(self, text: str, *args, **kwargs):
        if self.callback:
            return await self.callback.answer(text, *args, **kwargs)
        if self.message:
            return await self.message.reply_text(text, *args, **kwargs)
        return None

    async def _edit(self, text: str, *args, **kwargs):
        target = getattr(self.callback, "message", None) or self.message
        if not target:
            return None
        return await target.edit_text(text, *args, **kwargs)

    async def _target_user_id(self) -> tuple[int, str | None]:
        if self.callback and hasattr(self.callback, "data") and self.callback.data:
            parts = self.callback.data.split("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                return int(parts[1]), None
        return await extract_user(self.message)

    def _is_self(self, user_id: int) -> bool:
        return user_id == getattr(self.client, "me", None).id

    def _is_sudo_or_owner(self, user_id: int) -> bool:
        return user_id in SUDO or user_id == OWNER_ID

    async def _is_admin(self, user_id: int) -> bool:
        return user_id in await list_admins(self.chat.id)

    async def _safe_api(self, coro, *, on_not_admin: str | None = None):
        try:
            return await coro, None
        except ChatAdminRequired:
            return None, on_not_admin or "Please give me proper admin permissions."
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await coro, None
        except Exception as exc:
            return None, str(exc)

    async def _ensure_admin_restrict(self):
        perms = await member_permissions(self.chat.id, self.client.me.id)
        if "can_restrict_members" not in perms:
            await self._reply(self.strings("no_ban_permission"))
            return False
        return True

    # ---------- commands ----------
    async def purge(self):
        try:
            replied = self.message.reply_to_message
            await self.message.delete()
            if not replied:
                return await self._reply(self.strings("purge_no_reply"))

            cmd = self.message.command
            purge_to = replied.id + int(cmd[1]) if len(cmd) > 1 and cmd[1].isdigit() else self.message.id
            purge_to = min(purge_to, self.message.id)

            chat_id = self.chat.id
            message_ids: list[int] = []
            deleted = 0

            for mid in range(replied.id, purge_to):
                message_ids.append(mid)
                if len(message_ids) == 100:
                    _, err = await self._safe_api(
                        app.delete_messages(chat_id=chat_id, message_ids=message_ids, revoke=True)
                    )
                    if err:
                        return await self._reply(f"ERROR: {err}")
                    deleted += len(message_ids)
                    message_ids = []

            if message_ids:
                _, err = await self._safe_api(
                    app.delete_messages(chat_id=chat_id, message_ids=message_ids, revoke=True)
                )
                if err:
                    return await self._reply(f"ERROR: {err}")
                deleted += len(message_ids)

            await self._reply(self.strings("purge_success").format(del_total=deleted))
        except Exception as exc:
            await self._reply(f"ERROR: {exc}")

    async def kick(self, *, del_reply: bool = False):
        user_id, reason = await extract_user_and_reason(self.message)
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        if self._is_self(user_id):
            return await self._reply(self.strings("kick_self_err"))
        if self._is_sudo_or_owner(user_id):
            return await self._reply(self.strings("kick_sudo_err"))
        if await self._is_admin(user_id):
            return await self._reply(self.strings("kick_admin_err"))

        try:
            user = await app.get_users(user_id)
        except PeerIdInvalid:
            return await self._reply(self.strings("user_not_found"))

        msg = self.strings("kick_msg").format(
            mention=user.mention,
            id=user.id,
            kicker=self.from_user.mention if self.from_user else "Anon Admin",
            reasonmsg=reason or "-",
        )
        if del_reply and self.message.reply_to_message:
            await self.message.reply_to_message.delete()
        if not await self._ensure_admin_restrict():
            return
        _, err = await self._safe_api(self.chat.ban_member(user_id), on_not_admin=self.strings("no_ban_permission"))
        if err:
            return await self._reply(err)
        await self._reply(msg)
        await asyncio.sleep(1)
        _, err = await self._safe_api(self.chat.unban_member(user_id))
        if err:
            LOGGER.warning(f"Unban after kick failed: {err}")

    async def ban(self, *, del_reply: bool = False, temp_ban: int | None = None, reason: str | None = None):
        user_id, _ = await extract_user_and_reason(self.message, sender_chat=True)
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        if self._is_self(user_id):
            return await self._reply(self.strings("ban_self_err"))
        if self._is_sudo_or_owner(user_id):
            return await self._reply(self.strings("ban_sudo_err"))
        if await self._is_admin(user_id):
            return await self._reply(self.strings("ban_admin_err"))

        try:
            mention = (await app.get_users(user_id)).mention
        except PeerIdInvalid:
            return await self._reply(self.strings("user_not_found"))
        except IndexError:
            mention = getattr(self.message.reply_to_message.sender_chat, "title", "Anon") if self.message.reply_to_message else "Anon"

        msg = self.strings("ban_msg").format(
            mention=mention,
            id=user_id,
            banner=self.from_user.mention if self.from_user else "Anon",
        )
        if del_reply and self.message.reply_to_message:
            await self.message.reply_to_message.delete()
        if temp_ban is not None:
            msg += self.strings("banner_time").format(val=reason.split(None, 1)[0] if reason else "")
            temp_reason = reason.split(None, 1)[1] if reason and len(reason.split(None, 1)) > 1 else ""
            if temp_reason:
                msg += self.strings("banned_reason").format(reas=temp_reason)
            _, err = await self._safe_api(self.chat.ban_member(user_id, until_date=temp_ban))
            if err:
                return await self._reply(err)
            return await self._reply(msg)
        if reason:
            msg += self.strings("banned_reason").format(reas=reason)
        keyboard = ikb({"🚨 Unban 🚨": f"unban_{user_id}"})
        _, err = await self._safe_api(self.chat.ban_member(user_id), on_not_admin=self.strings("no_ban_permission"))
        if err:
            return await self._reply(err)
        await self._reply(msg, reply_markup=keyboard)

    async def unban(self):
        reply = self.message.reply_to_message
        if reply and getattr(reply, "sender_chat", None) and reply.sender_chat != self.chat.id:
            return await self._reply(self.strings("unban_channel_err"))

        if len(self.message.command) == 2:
            user = self.message.text.split(None, 1)[1]
        elif len(self.message.command) == 1 and reply:
            user = reply.from_user.id
        else:
            return await self._reply(self.strings("give_unban_user"))
        _, err = await self._safe_api(self.chat.unban_member(user), on_not_admin=self.strings("no_ban_permission"))
        if err:
            return await self._reply(err)
        umention = (await app.get_users(user)).mention
        await self._reply(self.strings("unban_success").format(umention=umention))

    async def list_ban(self):
        userid, msglink_reason = await extract_user_and_reason(self.message)
        if not userid or not msglink_reason:
            return await self._reply(self.strings("give_idban_with_msg_link"))
        if len(msglink_reason.split(" ")) == 1:
            return await self._reply(self.strings("give_reason_list_ban"))
        lreason = msglink_reason.split()
        messagelink, reason = lreason[0], " ".join(lreason[1:])
        if not re.search(r"(https?://)?t(telegram)?\.me/\w+/\d+", messagelink):
            return await self._reply(self.strings("invalid_tg_link"))
        if self._is_self(userid):
            return await self._reply(self.strings("ban_self_err"))
        if self._is_sudo_or_owner(userid):
            return await self._reply(self.strings("ban_sudo_err"))
        splitted = messagelink.split("/")
        uname, mid = splitted[-2], int(splitted[-1])
        m = await self._reply(self.strings("multiple_ban_progress"))
        try:
            msgtext = (await app.get_messages(uname, mid)).text
            gusernames = re.findall(r"@\w+", msgtext)
        except Exception:
            return await self._edit(self.strings("failed_get_uname"))
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
        msg = self.strings("listban_msg").format(
            mention=mention, uid=userid, frus=self.from_user.mention, ct=count, reas=reason
        )
        await self._edit(msg)

    async def list_unban(self):
        userid, msglink = await extract_user_and_reason(self.message)
        if not userid or not msglink:
            return await self._reply(self.strings("give_idunban_with_msg_link"))
        if not re.search(r"(https?://)?t(telegram)?\.me/\w+/\d+", msglink):
            return await self._reply(self.strings("invalid_tg_link"))
        splitted = msglink.split("/")
        uname, mid = splitted[-2], int(splitted[-1])
        m = await self._reply(self.strings("multiple_unban_progress"))
        try:
            msgtext = (await app.get_messages(uname, mid)).text
            gusernames = re.findall(r"@\w+", msgtext)
        except Exception:
            return await self._edit(self.strings("failed_get_uname"))
        count = 0
        for username in gusernames:
            try:
                await app.unban_chat_member(username.strip("@"), userid)
                await asyncio.sleep(1)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception:
                continue
            count += 1
        mention = (await app.get_users(userid)).mention
        msg = self.strings("listunban_msg").format(
            mention=mention, uid=userid, frus=self.from_user.mention, ct=count
        )
        await self._edit(msg)

    async def delete_replied(self):
        if not self.message.reply_to_message:
            return await self._reply(self.strings("delete_no_reply"))
        try:
            await self.message.reply_to_message.delete()
            await self.message.delete()
        except Exception:
            await self._reply(self.strings("no_delete_perm"))

    async def promote(self, *, full: bool = False):
        try:
            user_id = await extract_user(self.message)
            umention = (await self.client.get_users(user_id)).mention
        except Exception:
            return await self._reply(self.strings("invalid_id_uname"))
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        bot = (await self.client.get_chat_member(self.chat.id, self.client.me.id)).privileges
        if self._is_self(user_id):
            return await self._reply(self.strings("promote_self_err"))
        if not bot:
            return await self._reply("I'm not an admin in this chat.")
        if not bot.can_promote_members:
            return await self._reply(self.strings("no_promote_perm"))
        try:
            privileges = ChatPrivileges(
                can_change_info=bot.can_change_info if full else False,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=bot.can_promote_members if full else False,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            )
            await self.chat.promote_member(user_id=user_id, privileges=privileges)
            await self._reply(
                self.strings("full_promote" if full else "normal_promote").format(umention=umention)
            )
        except Exception as exc:
            await self._reply(str(exc))

    async def demote(self):
        user_id = await extract_user(self.message)
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        if self._is_self(user_id):
            return await self._reply(self.strings("demote_self_err"))
        if self._is_sudo_or_owner(user_id):
            return await self._reply(self.strings("demote_sudo_err"))
        try:
            await self.chat.promote_member(
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
            )
            umention = (await app.get_users(user_id)).mention
            await self._reply(f"Demoted! {umention}")
        except ChatAdminRequired:
            await self._reply("Please give permission to demote members..")
        except Exception as exc:
            await self._reply(str(exc))

    async def pin(self, *, unpin: bool = False):
        if not self.message.reply_to_message:
            return await self._reply(self.strings("pin_no_reply"))
        r = self.message.reply_to_message
        try:
            preview = pyro_types.LinkPreviewOptions(is_disabled=True)
            if unpin:
                await r.unpin()
                return await self._reply(self.strings("unpin_success").format(link=r.link), link_preview_options=preview)
            await r.pin(disable_notification=True)
            await self._reply(self.strings("pin_success").format(link=r.link), link_preview_options=preview)
        except ChatAdminRequired:
            await self._reply(self.strings("pin_no_perm"), link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True))
        except Exception as exc:
            await self._reply(str(exc))

    async def mute(self, *, temp_mute: int | None = None, reason: str | None = None):
        try:
            user_id, _ = await extract_user_and_reason(self.message)
        except Exception as exc:
            return await self._reply(f"ERROR: {exc}")
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        if self._is_self(user_id):
            return await self._reply(self.strings("mute_self_err"))
        if self._is_sudo_or_owner(user_id):
            return await self._reply(self.strings("mute_sudo_err"))
        if await self._is_admin(user_id):
            return await self._reply(self.strings("mute_admin_err"))

        mention = (await app.get_users(user_id)).mention
        keyboard = ikb({"🚨 Unmute 🚨": f"unmute_{user_id}"})
        msg = self.strings("mute_msg").format(
            mention=mention,
            muter=self.from_user.mention if self.from_user else "Anon",
        )
        if temp_mute is not None:
            time_value = reason.split(None, 1)[0] if reason else ""
            temp_reason = reason.split(None, 1)[1] if reason and len(reason.split(None, 1)) > 1 else ""
            msg += self.strings("muted_time").format(val=time_value)
            if temp_reason:
                msg += self.strings("banned_reason").format(reas=temp_reason)
            if len(time_value[:-1]) < 3:
                _, err = await self._safe_api(
                    self.chat.restrict_member(user_id, permissions=empty_chat_permissions(), until_date=temp_mute),
                    on_not_admin=self.strings("no_ban_permission"),
                )
                if err:
                    return await self._reply(err)
                return await self._reply(msg, reply_markup=keyboard)
            return await self._reply(self.strings("no_more_99"))

        if reason:
            msg += self.strings("banned_reason").format(reas=reason)
        _, err = await self._safe_api(
            self.chat.restrict_member(user_id, permissions=empty_chat_permissions()),
            on_not_admin=self.strings("no_ban_permission"),
        )
        if err:
            return await self._reply(err)
        await self._reply(msg, reply_markup=keyboard)

    async def unmute(self):
        user_id = await extract_user(self.message)
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        _, err = await self._safe_api(self.chat.unban_member(user_id))
        if err:
            return await self._reply(err)
        umention = (await app.get_users(user_id)).mention
        await self._reply(self.strings("unmute_msg").format(umention=umention))

    async def warn(self, *, del_reply: bool = False):
        try:
            user_id, reason = await extract_user_and_reason(self.message)
        except UsernameNotOccupied:
            return await self._reply("Sorry, i didn't know that user.")
        chat_id = self.chat.id
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        if self._is_self(user_id):
            return await self._reply(self.strings("warn_self_err"))
        if self._is_sudo_or_owner(user_id):
            return await self._reply(self.strings("warn_sudo_err"))
        if await self._is_admin(user_id):
            return await self._reply(self.strings("warn_admin_err"))

        user, warns = await asyncio.gather(
            app.get_users(user_id),
            get_warn(chat_id, await int_to_alpha(user_id)),
        )
        mention = user.mention
        keyboard = ikb({self.strings("rm_warn_btn"): f"unwarn_{user_id}"})
        warns = warns["warns"] if warns else 0
        if del_reply and self.message.reply_to_message:
            await self.message.reply_to_message.delete()
        if warns >= 2:
            _, err = await self._safe_api(self.chat.ban_member(user_id))
            if err:
                return await self._reply(err)
            await self._reply(self.strings("exceed_warn_msg").format(mention=mention))
            await remove_warns(chat_id, await int_to_alpha(user_id))
            return
        warn = {"warns": warns + 1}
        msg = self.strings("warn_msg").format(
            mention=mention,
            warner=self.from_user.mention if self.from_user else "Anon",
            reas=reason or "No Reason Provided.",
            twarn=warns + 1,
        )
        await self._reply(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)

    async def remove_warning(self):
        chat_id = self.chat.id
        from_user = self.callback.from_user
        permissions = await member_permissions(chat_id, from_user.id)
        if "can_restrict_members" not in permissions:
            return await self.callback.answer(
                self.strings("no_permission_error").format(permissions=permissions),
                show_alert=True,
            )
        user_id = int(self.callback.data.split("_")[1])
        warns = await get_warn(chat_id, await int_to_alpha(user_id))
        warns = warns.get("warns", 0) if warns else 0
        if not warns:
            return await self.callback.answer(
                self.strings("user_no_warn").format(
                    mention=self.callback.message.reply_to_message.from_user.id
                )
            )
        warn = {"warns": warns - 1}
        await add_warn(chat_id, await int_to_alpha(user_id), warn)
        text = self.callback.message.text.markdown
        text = f"~~{text}~~\n\n"
        text += self.strings("unwarn_msg").format(mention=from_user.mention)
        await self.callback.message.edit(text)

    async def unmute_callback(self):
        chat_id = self.chat.id
        from_user = self.callback.from_user
        permissions = await member_permissions(chat_id, from_user.id)
        if "can_restrict_members" not in permissions:
            return await self.callback.answer(
                self.strings("no_permission_error").format(permissions=permissions),
                show_alert=True,
            )
        user_id = int(self.callback.data.split("_")[1])
        text = self.callback.message.text.markdown
        text = f"~~{text}~~\n\n"
        text += self.strings("rmmute_msg").format(mention=from_user.mention)
        _, err = await self._safe_api(self.chat.unban_member(user_id))
        if err:
            return await self.callback.answer(str(err))
        await self.callback.message.edit(text)

    async def unban_callback(self):
        chat_id = self.chat.id
        from_user = self.callback.from_user
        permissions = await member_permissions(chat_id, from_user.id)
        if "can_restrict_members" not in permissions:
            return await self.callback.answer(
                self.strings("no_permission_error").format(permissions=permissions),
                show_alert=True,
            )
        user_id = int(self.callback.data.split("_")[1])
        text = self.callback.message.text.markdown
        text = f"~~{text}~~\n\n"
        text += self.strings("unban_msg").format(mention=from_user.mention)
        _, err = await self._safe_api(self.chat.unban_member(user_id))
        if err:
            return await self.callback.answer(str(err))
        await self.callback.message.edit(text)

    async def remove_warnings(self):
        if not self.message.reply_to_message:
            return await self._reply(self.strings("reply_to_rm_warn"))
        user_id = self.message.reply_to_message.from_user.id
        mention = self.message.reply_to_message.from_user.mention
        chat_id = self.chat.id
        warns = await get_warn(chat_id, await int_to_alpha(user_id))
        warns = warns.get("warns", 0) if warns else 0
        if warns == 0 or not warns:
            await self._reply(self.strings("user_no_warn").format(mention=mention))
        else:
            await remove_warns(chat_id, await int_to_alpha(user_id))
            await self._reply(self.strings("rmwarn_msg").format(mention=mention))

    async def check_warns(self):
        if not self.message.from_user:
            return
        user_id = await extract_user(self.message)
        if not user_id:
            return await self._reply(self.strings("user_not_found"))
        warns = await get_warn(self.chat.id, await int_to_alpha(user_id))
        mention = (await app.get_users(user_id)).mention
        warns = warns.get("warns", 0) if warns else 0
        if not warns:
            return await self._reply(self.strings("user_no_warn").format(mention=mention))
        return await self._reply(
            self.strings("ch_warn_msg").format(mention=mention, warns=warns)
        )

    async def report(self):
        if len(self.message.text.split()) <= 1 and not self.message.reply_to_message:
            return await self._reply(self.strings("report_no_reply"))
        reply = self.message.reply_to_message or self.message
        reply_id = (reply.from_user.id if reply.from_user else reply.sender_chat.id)
        user_id = self.message.from_user.id if self.message.from_user else self.message.sender_chat.id
        if reply_id == user_id:
            return await self._reply(self.strings("report_self_err"))
        list_of_admins = await list_admins(self.chat.id)
        linked_chat = (await app.get_chat(self.chat.id)).linked_chat
        if linked_chat is None:
            if reply_id in list_of_admins or reply_id == self.chat.id:
                return await self._reply(self.strings("reported_is_admin"))
        elif reply_id in list_of_admins or reply_id == self.chat.id or reply_id == linked_chat.id:
            return await self._reply(self.strings("reported_is_admin"))
        user_mention = reply.from_user.mention if reply.from_user else reply.sender_chat.title
        text = self.strings("report_msg").format(user_mention=user_mention)
        admin_data = [
            m
            async for m in app.get_chat_members(
                self.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
            )
        ]
        for admin in admin_data:
            if admin.user.is_bot or admin.user.is_deleted:
                continue
            text += f"<a href='tg://user?id={admin.user.id}'>\u2063</a>"
        await reply.reply(text)

    async def set_chat_title(self):
        if len(self.message.command) < 2:
            return await self._reply(f"**Usage:**\n/{self.message.command[0]} NEW NAME")
        old_title = self.chat.title
        new_title = self.message.text.split(None, 1)[1]
        _, err = await self._safe_api(self.chat.set_title(new_title))
        if err:
            return await self._reply(err)
        await self._reply(
            f"Successfully Changed Group Title From {old_title} To {new_title}"
        )

    async def set_user_title(self):
        if not self.message.reply_to_message:
            return await self._reply("Reply to user's message to set his admin title")
        if not self.message.reply_to_message.from_user:
            return await self._reply("I can't change admin title of an unknown entity")
        if len(self.message.command) < 2:
            return await self._reply("**Usage:**\n/set_user_title NEW ADMINISTRATOR TITLE")
        title = self.message.text.split(None, 1)[1]
        from_user = self.message.reply_to_message.from_user
        _, err = await self._safe_api(app.set_administrator_title(self.chat.id, from_user.id, title))
        if err:
            return await self._reply(err)
        await self._reply(f"Successfully Changed {from_user.mention}'s Admin Title To {title}")

    async def set_chat_photo(self):
        reply = self.message.reply_to_message
        if not reply:
            return await self._reply("Reply to a photo to set it as chat_photo")
        file = reply.document or reply.photo
        if not file:
            return await self._reply("Reply to a photo or document to set it as chat_photo")
        if getattr(file, "file_size", 0) > 5000000:
            return await self._reply("File size too large.")
        photo = await reply.download()
        _, err = await self._safe_api(self.chat.set_photo(photo=photo))
        try:
            if err:
                return await self._reply(f"Failed changed group photo. ERROR: {err}")
            await self._reply("Successfully Changed Group Photo")
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.remove(photo)

    async def mentionall(self):
        member = await self.chat.get_member(self.message.from_user.id)
        if member.status not in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        ):
            return await app.send_message(
                self.chat.id,
                "Admins only can do that !",
                reply_parameters=pyro_types.ReplyParameters(message_id=self.message.id),
            )
        total = []
        async for m in app.get_chat_members(self.chat.id):
            if m.user.username:
                total.append(f"@{m.user.username}")
            else:
                total.append(m.user.mention)
        for i in range(0, len(total), 4):
            message = " ".join(total[i : i + 4])
            await app.send_message(
                self.chat.id,
                message,
                message_thread_id=getattr(self.message, "message_thread_id", None),
            )


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
    await AdminManager(app, message=ctx, strings=strings).purge()


# Kick members
@app.on_cmd(["kick", "dkick"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def kickFunc(client: Client, ctx: Message, strings) -> "Message":
    await AdminManager(client, message=ctx, strings=strings).kick(del_reply=ctx.command[0][0] == "d")


# Ban/DBan/TBan User
@app.on_cmd(["ban", "dban", "tban"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def banFunc(client, message, strings):
    reason = ""
    temp_ban = None
    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        reason = f"{time_value} {temp_reason}".strip()
    await AdminManager(client, message=message, strings=strings).ban(
        del_reply=message.command[0][0] == "d",
        temp_ban=temp_ban,
        reason=reason or None,
    )


# Unban members
@app.on_cmd("unban", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def unban_func(_, message, strings):
    await AdminManager(app, message=message, strings=strings).unban()


# Ban users listed in a message
@app.on_message(
    (filters.user(SUDO) | filters.user(OWNER_ID)) & filters.command("listban", COMMAND_HANDLER) & filters.group
)
@use_chat_lang()
async def list_ban_(c, message, strings):
    await AdminManager(c, message=message, strings=strings).list_ban()


# Unban users listed in a message
@app.on_message(
    (filters.user(SUDO) | filters.user(OWNER_ID)) & filters.command("listunban", COMMAND_HANDLER) & filters.group
)
@use_chat_lang()
async def list_unban(_, message, strings):
    await AdminManager(app, message=message, strings=strings).list_unban()


# Delete messages
@app.on_cmd("del", group_only=True)
@app.adminsOnly("can_delete_messages")
@use_chat_lang()
async def deleteFunc(_, message, strings):
    await AdminManager(app, message=message, strings=strings).delete_replied()


# Promote Members
@app.on_cmd(["promote", "fullpromote"], self_admin=True, group_only=True)
@app.adminsOnly("can_promote_members")
@use_chat_lang()
async def promoteFunc(client, message, strings):
    await AdminManager(client, message=message, strings=strings).promote(full=message.command[0][0] == "f")


# Demote Member
@app.on_cmd("demote", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def demote(client, message, strings):
    await AdminManager(client, message=message, strings=strings).demote()


# Pin Messages
@app.on_cmd(["pin", "unpin"])
@app.adminsOnly("can_pin_messages")
@use_chat_lang()
async def pin(_, message, strings):
    await AdminManager(app, message=message, strings=strings).pin(unpin=message.command[0][0] == "u")


# Mute members
@app.on_cmd(["mute", "tmute"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def mute(client, message, strings):
    reason = ""
    temp_mute = None
    if message.command[0] == "tmute":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        reason = f"{time_value} {temp_reason}".strip()
    await AdminManager(client, message=message, strings=strings).mute(
        temp_mute=temp_mute,
        reason=reason or None,
    )


# Unmute members
@app.on_cmd("unmute", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def unmute(_, message, strings):
    await AdminManager(app, message=message, strings=strings).unmute()


@app.on_cmd(["warn", "dwarn"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def warn_user(client, message, strings):
    await AdminManager(client, message=message, strings=strings).warn(del_reply=message.command[0][0] == "d")


@app.on_callback_query(filters.regex("unwarn_"))
@use_chat_lang()
async def remove_warning(_, cq, strings):
    await AdminManager(app, callback=cq, strings=strings).remove_warning()


@app.on_callback_query(filters.regex("unmute_"))
@use_chat_lang()
async def unmute_user(_, cq, strings):
    await AdminManager(app, callback=cq, strings=strings).unmute_callback()


@app.on_callback_query(filters.regex("unban_"))
@use_chat_lang()
async def unban_user(_, cq, strings):
    await AdminManager(app, callback=cq, strings=strings).unban_callback()


# Remove Warn
@app.on_cmd("rmwarn", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def remove_warnings(_, message, strings):
    await AdminManager(app, message=message, strings=strings).remove_warnings()


# Warns
@app.on_cmd("warns", group_only=True)
@use_chat_lang()
async def check_warns(_, message, strings):
    await AdminManager(app, message=message, strings=strings).check_warns()


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
async def report_user(_, ctx: Message, strings) -> "Message":
    await AdminManager(app, message=ctx, strings=strings).report()


@app.on_cmd("set_chat_title", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
async def set_chat_title(_, ctx: Message):
    await AdminManager(app, message=ctx).set_chat_title()


@app.on_cmd("set_user_title", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
async def set_user_title(_, ctx: Message):
    await AdminManager(app, message=ctx).set_user_title()


@app.on_cmd("set_chat_photo", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
async def set_chat_photo(_, ctx: Message):
    await AdminManager(app, message=ctx).set_chat_photo()


@app.on_message(filters.group & filters.command("mentionall", COMMAND_HANDLER))
async def mentionall(app: Client, msg: Message):
    await AdminManager(app, message=msg).mentionall()
