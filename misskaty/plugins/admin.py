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
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    PeerIdInvalid,
    UsernameNotOccupied,
)
from pyrogram.types import ChatPermissions, ChatMember, ChatPrivileges, Message

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
from misskaty.vars import COMMAND_HANDLER, SUDO

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
        except:
            pass


# Purge CMD
@app.on_cmd("purge")
@app.adminsOnly("can_delete_messages")
@use_chat_lang()
async def purge(_, ctx: Message, strings):
    try:
        repliedmsg = ctx.reply_to_message
        await ctx.delete_msg()

        if not repliedmsg:
            return await ctx.reply_msg(strings("purge_no_reply"))

        cmd = ctx.command
        if len(cmd) > 1 and cmd[1].isdigit():
            purge_to = repliedmsg.id + int(cmd[1])
            purge_to = min(purge_to, ctx.id)
        else:
            purge_to = ctx.id

        chat_id = ctx.chat.id
        message_ids = []
        del_total = 0

        for message_id in range(
            repliedmsg.id,
            purge_to,
        ):
            message_ids.append(message_id)

            # Max message deletion limit is 100
            if len(message_ids) == 100:
                await app.delete_messages(
                    chat_id=chat_id,
                    message_ids=message_ids,
                    revoke=True,  # For both sides
                )
                del_total += len(message_ids)
                # To delete more than 100 messages, start again
                message_ids = []

        # Delete if any messages left
        if len(message_ids) > 0:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,
            )
            del_total += len(message_ids)
        await ctx.reply_msg(strings("purge_success").format(del_total=del_total))
    except Exception as err:
        await ctx.reply_msg(f"ERROR: {err}")


# Kick members
@app.on_cmd(["kick", "dkick"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def kickFunc(client: Client, ctx: Message, strings) -> "Message":
    user_id, reason = await extract_user_and_reason(ctx)
    if not user_id:
        return await ctx.reply_msg(strings("user_not_found"))
    if user_id == client.me.id:
        return await ctx.reply_msg(strings("kick_self_err"))
    if user_id in SUDO:
        return await ctx.reply_msg(strings("kick_sudo_err"))
    if user_id in (await list_admins(ctx.chat.id)):
        return await ctx.reply_msg(strings("kick_admin_err"))
    try:
        user = await app.get_users(user_id)
    except PeerIdInvalid:
        return await ctx.reply_msg(strings("user_not_found"))
    msg = strings("kick_msg").format(
        mention=user.mention,
        id=user.id,
        kicker=ctx.from_user.mention if ctx.from_user else "Anon Admin",
        reasonmsg=reason or "-",
    )
    if ctx.command[0][0] == "d":
        await ctx.reply_to_message.delete_msg()
    try:
        await ctx.chat.ban_member(user_id)
        await ctx.reply_msg(msg)
        await asyncio.sleep(1)
        await ctx.chat.unban_member(user_id)
    except ChatAdminRequired:
        await ctx.reply_msg(strings("no_ban_permission"))
    except Exception as e:
        await ctx.reply_msg(str(e))


# Ban/DBan/TBan User
@app.on_cmd(["ban", "dban", "tban"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def banFunc(client, message, strings):
    try:
        user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    except UsernameNotOccupied:
        return await message.reply_msg("Sorry, i didn't know that user.") 

    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if user_id == client.me.id:
        return await message.reply_text(strings("ban_self_err"))
    if user_id in SUDO:
        return await message.reply_text(strings("ban_sudo_err"))
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(strings("ban_admin_err"))

    try:
        mention = (await app.get_users(user_id)).mention
    except PeerIdInvalid:
        return await message.reply_text(strings("user_not_found"))
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "Anon"
        )

    msg = strings("ban_msg").format(
        mention=mention,
        id=user_id,
        banner=message.from_user.mention if message.from_user else "Anon",
    )
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += strings("banner_time").format(val=time_value)
        if temp_reason:
            msg += strings("banned_reason").format(reas=temp_reason)
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                await message.reply_text(msg)
            else:
                await message.reply_text(strings("no_more_99"))
        except AttributeError:
            pass
        return
    if reason:
        msg += strings("banned_reason").format(reas=reason)
    keyboard = ikb({"🚨 Unban 🚨": f"unban_{user_id}"})
    try:
        await message.chat.ban_member(user_id)
        await message.reply_msg(msg, reply_markup=keyboard)
    except ChatAdminRequired:
        await message.reply("Please give me permission to banned members..!!!")
    except Exception as e:
        await message.reply_msg(str(e))


# Unban members
@app.on_cmd("unban", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def unban_func(_, message, strings):
    # we don't need reasons for unban, also, we
    # don't need to get "text_mention" entity, because
    # normal users won't get text_mention if the user
    # they want to unban is not in the group.
    reply = message.reply_to_message

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text(strings("unban_channel_err"))

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await message.reply_msg(strings("give_unban_user"))
    try:
        await message.chat.unban_member(user)
        umention = (await app.get_users(user)).mention
        await message.reply_msg(strings("unban_success").format(umention=umention))
    except PeerIdInvalid:
        await message.reply_msg(strings("unknown_id", context="general"))
    except ChatAdminRequired:
        await message.reply("Please give me permission to unban members..!!!")
    except Exception as e:
        await message.reply_msg(str(e))


# Ban users listed in a message
@app.on_message(
    filters.user(SUDO) & filters.command("listban", COMMAND_HANDLER) & filters.group
)
@use_chat_lang()
async def list_ban_(c, message, strings):
    userid, msglink_reason = await extract_user_and_reason(message)
    if not userid or not msglink_reason:
        return await message.reply_text(strings("give_idban_with_msg_link"))
    if len(msglink_reason.split(" ")) == 1:  # message link included with the reason
        return await message.reply_text(strings("give_reason_list_ban"))
    # seperate messge link from reason
    lreason = msglink_reason.split()
    messagelink, reason = lreason[0], " ".join(lreason[1:])

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", messagelink
    ):  # validate link
        return await message.reply_text(strings("invalid_tg_link"))

    if userid == c.me.id:
        return await message.reply_text(strings("ban_self_err"))
    if userid in SUDO:
        return await message.reply_text(strings("ban_sudo_err"))
    splitted = messagelink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(strings("multiple_ban_progress"))
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\w+", msgtext)
    except:
        return await m.edit_text(strings("failed_get_uname"))
    count = 0
    for username in gusernames:
        try:
            await app.ban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention

    msg = strings("listban_msg").format(
        mention=mention,
        uid=userid,
        frus=message.from_user.mention,
        ct=count,
        reas=reason,
    )
    await m.edit_text(msg)


# Unban users listed in a message
@app.on_message(
    filters.user(SUDO) & filters.command("listunban", COMMAND_HANDLER) & filters.group
)
@use_chat_lang()
async def list_unban(_, message, strings):
    userid, msglink = await extract_user_and_reason(message)
    if not userid or not msglink:
        return await message.reply_text(strings("give_idunban_with_msg_link"))

    if not re.search(r"(https?://)?t(elegram)?\.me/\w+/\d+", msglink):  # validate link
        return await message.reply_text(strings("invalid_tg_link"))

    splitted = msglink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(strings("multiple_unban_progress"))
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\w+", msgtext)
    except:
        return await m.edit_text(strings("failed_get_uname"))
    count = 0
    for username in gusernames:
        try:
            await app.unban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
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
    except:
        await message.reply(strings("no_delete_perm"))


# Promote Members
@app.on_cmd(["promote", "fullpromote"], self_admin=True, group_only=True)
@app.adminsOnly("can_promote_members")
@use_chat_lang()
async def promoteFunc(client, message, strings):
    try:
        user_id = await extract_user(message)
        umention = (await client.get_users(user_id)).mention
    except:
        return await message.reply(strings("invalid_id_uname"))
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if user_id == client.me.id:
        return await message.reply_msg(strings("promote_self_err"))
    if not bot:
        return await message.reply_msg("I'm not an admin in this chat.")
    if not bot.can_promote_members:
        return await message.reply_msg(strings("no_promote_perm"))
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
        await message.reply_msg(strings("normal_promote").format(umention=umention))
    except Exception as err:
        await message.reply_msg(err)


# Demote Member
@app.on_cmd("demote", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def demote(client, message, strings):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if user_id == client.me.id:
        return await message.reply_text(strings("demote_self_err"))
    if user_id in SUDO:
        return await message.reply_text(strings("demote_sudo_err"))
    try:
        await message.chat.promote_member(
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
        await message.reply_text(f"Demoted! {umention}")
    except ChatAdminRequired:
        await message.reply("Please give permission to demote members..")
    except Exception as e:
        await message.reply_msg(str(e))


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
                disable_web_page_preview=True,
            )
        await r.pin(disable_notification=True)
        await message.reply(
            strings("pin_success").format(link=r.link),
            disable_web_page_preview=True,
        )
    except ChatAdminRequired:
        await message.reply(
            strings("pin_no_perm"),
            disable_web_page_preview=True,
        )
    except Exception as e:
        await message.reply_msg(str(e))


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
    if user_id == client.me.id:
        return await message.reply_text(strings("mute_self_err"))
    if user_id in SUDO:
        return await message.reply_text(strings("mute_sudo_err"))
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(strings("mute_admin_err"))
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨 Unmute 🚨": f"unmute_{user_id}"})
    msg = strings("mute_msg").format(
        mention=mention,
        muter=message.from_user.mention if message.from_user else "Anon",
    )
    if message.command[0] == "tmute":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += strings("muted_time").format(val=time_value)
        if temp_reason:
            msg += strings("banned_reason").format(reas=temp_reason)
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(all_perms=False),
                    until_date=temp_mute,
                )
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text(strings("no_more_99"))
        except AttributeError:
            pass
        return
    if reason:
        msg += strings("banned_reason").format(reas=reason)
    try:
        await message.chat.restrict_member(user_id, permissions=ChatPermissions(all_perms=False))
        await message.reply_text(msg, reply_markup=keyboard)
    except Exception as e:
        await message.reply_msg(str(e))


# Unmute members
@app.on_cmd("unmute", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def unmute(_, message, strings):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    try:
        await message.chat.unban_member(user_id)
        umention = (await app.get_users(user_id)).mention
        await message.reply_msg(strings("unmute_msg").format(umention=umention))
    except Exception as e:
        await message.reply_msg(str(e))


@app.on_cmd(["warn", "dwarn"], self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def warn_user(client, message, strings):
    try:
        user_id, reason = await extract_user_and_reason(message)
    except UsernameNotOccupied:
        return await message.reply_msg("Sorry, i didn't know that user.")
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text(strings("user_not_found"))
    if user_id == client.me.id:
        return await message.reply_text(strings("warn_self_err"))
    if user_id in SUDO:
        return await message.reply_text(strings("warn_sudo_err"))
    if user_id in (await list_admins(chat_id)):
        return await message.reply_text(strings("warn_admin_err"))
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({strings("rm_warn_btn"): f"unwarn_{user_id}"})
    warns = warns["warns"] if warns else 0
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(strings("exceed_warn_msg").format(mention=mention))
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = strings("warn_msg").format(
            mention=mention,
            warner=message.from_user.mention if message.from_user else "Anon",
            reas=reason or "No Reason Provided.",
            twarn=warns + 1,
        )
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_"))
@use_chat_lang()
async def remove_warning(_, cq, strings):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            strings("no_permission_error").format(permissions=permission),
            show_alert=True,
        )
    user_id = int(cq.data.split("_")[1])
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer(
            strings("user_no_warn").format(
                mention=cq.message.reply_to_message.from_user.id
            )
        )
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += strings("unwarn_msg").format(mention=from_user.mention)
    await cq.message.edit(text)


@app.on_callback_query(filters.regex("unmute_"))
@use_chat_lang()
async def unmute_user(_, cq, strings):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            strings("no_permission_error").format(permissions=permission),
            show_alert=True,
        )
    user_id = int(cq.data.split("_")[1])
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += strings("rmmute_msg").format(mention=from_user.mention)
    try:
        await cq.message.chat.unban_member(user_id)
        await cq.message.edit(text)
    except Exception as e:
        await cq.answer(str(e))


@app.on_callback_query(filters.regex("unban_"))
@use_chat_lang()
async def unban_user(_, cq, strings):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            strings("no_permission_error").format(permissions=permission),
            show_alert=True,
        )
    user_id = int(cq.data.split("_")[1])
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += strings("unban_msg").format(mention=from_user.mention)
    try:
        await cq.message.chat.unban_member(user_id)
        await cq.message.edit(text)
    except Exception as e:
        await cq.answer(str(e))


# Remove Warn
@app.on_cmd("rmwarn", self_admin=True, group_only=True)
@app.adminsOnly("can_restrict_members")
@use_chat_lang()
async def remove_warnings(_, message, strings):
    if not message.reply_to_message:
        return await message.reply_text(strings("reply_to_rm_warn"))
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
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
    if warns:
        warns = warns["warns"]
    else:
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
async def report_user(_, ctx: Message, strings) -> "Message":
    if not ctx.reply_to_message:
        return await ctx.reply_msg(strings("report_no_reply"))
    reply = ctx.reply_to_message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = ctx.from_user.id if ctx.from_user else ctx.sender_chat.id
    if reply_id == user_id:
        return await ctx.reply_msg(strings("report_self_err"))

    list_of_admins = await list_admins(ctx.chat.id)
    linked_chat = (await app.get_chat(ctx.chat.id)).linked_chat
    if linked_chat is None:
        if reply_id in list_of_admins or reply_id == ctx.chat.id:
            return await ctx.reply_msg(strings("reported_is_admin"))
    elif (
        reply_id in list_of_admins
        or reply_id == ctx.chat.id
        or reply_id == linked_chat.id
    ):
        return await ctx.reply_msg(strings("reported_is_admin"))
    user_mention = (
        reply.from_user.mention if reply.from_user else reply.sender_chat.title
    )
    text = strings("report_msg").format(user_mention=user_mention)
    admin_data = [
        m
        async for m in app.get_chat_members(
            ctx.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        )
    ]
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            # return bots or deleted admins
            continue
        text += f"<a href='tg://user?id={admin.user.id}'>\u2063</a>"
    await ctx.reply_msg(text, reply_to_message_id=ctx.reply_to_message.id)


@app.on_cmd("set_chat_title", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
async def set_chat_title(_, ctx: Message):
    if len(ctx.command) < 2:
        return await ctx.reply_text(f"**Usage:**\n/{ctx.command[0]} NEW NAME")
    old_title = ctx.chat.title
    new_title = ctx.text.split(None, 1)[1]
    try:
        await ctx.chat.set_title(new_title)
        await ctx.reply_text(
            f"Successfully Changed Group Title From {old_title} To {new_title}"
        )
    except Exception as e:
        await ctx.reply_msg(str(e))


@app.on_cmd("set_user_title", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
async def set_user_title(_, ctx: Message):
    if not ctx.reply_to_message:
        return await ctx.reply_text("Reply to user's message to set his admin title")
    if not ctx.reply_to_message.from_user:
        return await ctx.reply_text("I can't change admin title of an unknown entity")
    chat_id = ctx.chat.id
    from_user = ctx.reply_to_message.from_user
    if len(ctx.command) < 2:
        return await ctx.reply_text(
            "**Usage:**\n/set_user_title NEW ADMINISTRATOR TITLE"
        )
    title = ctx.text.split(None, 1)[1]
    try:
        await app.set_administrator_title(chat_id, from_user.id, title)
        await ctx.reply_text(
            f"Successfully Changed {from_user.mention}'s Admin Title To {title}"
        )
    except Exception as e:
        await ctx.reply_msg(str(e))


@app.on_cmd("set_chat_photo", self_admin=True, group_only=True)
@app.adminsOnly("can_change_info")
async def set_chat_photo(_, ctx: Message):
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
    try:
        await ctx.chat.set_photo(photo=photo)
        await ctx.reply_text("Successfully Changed Group Photo")
    except Exception as err:
        await ctx.reply(f"Failed changed group photo. ERROR: {err}")
    os.remove(photo)


@app.on_message(filters.group & filters.command('mentionall', COMMAND_HANDLER))
async def mentionall(app: Client, msg: Message):
    user = await msg.chat.get_member(msg.from_user.id)
    if user.status in (enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR):
        total = []
        async for member in app.get_chat_members(msg.chat.id):
            member: ChatMember
            if member.user.username:
                total.append(f'@{member.user.username}')
            else:
                total.append(member.user.mention())

        NUM = 4
        for i in range(0, len(total), NUM):
            message = ' '.join(total[i:i+NUM])
            await app.send_message(msg.chat.id, message, message_thread_id=msg.message_thread_id)
    else:
        await app.send_message(msg.chat.id, 'Admins only can do that !', reply_to_message_id=msg.id)
