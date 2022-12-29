import asyncio, re
from logging import getLogger
from misskaty import app
from misskaty.helper.functions import (
    extract_user_and_reason,
    time_converter,
    extract_user,
    int_to_alpha,
)
from time import time
from pyrogram import filters, enums
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import ChatPermissions
from misskaty.core.decorator.permissions import (
    adminsOnly,
    admins_in_chat,
    list_admins,
    member_permissions,
)
from misskaty.core.decorator.errors import capture_err
from misskaty.core.keyboard import ikb
from misskaty.vars import SUDO, COMMAND_HANDLER
from database.warn_db import get_warn, remove_warns, add_warn

LOGGER = getLogger(__name__)

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
"""


# Admin cache reload
@app.on_chat_member_updated()
async def admin_cache_func(_, cmu):
    if cmu.old_chat_member and cmu.old_chat_member.promoted_by:
        admins_in_chat[cmu.chat.id] = {
            "last_updated_at": time(),
            "data": [member.user.id async for member in app.get_chat_members(cmu.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)],
        }
        LOGGER.info(f"Updated admin cache for {cmu.chat.id} [{cmu.chat.title}]")


# Purge CMD
@app.on_message(filters.command("purge", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_delete_messages")
async def purge(_, message):
    repliedmsg = message.reply_to_message
    await message.delete()

    if not repliedmsg:
        return await message.reply_text("Reply to a message to purge from.")

    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purge_to = repliedmsg.id + int(cmd[1])
        if purge_to > message.id:
            purge_to = message.id
    else:
        purge_to = message.id

    chat_id = message.chat.id
    message_ids = []
    del_total = 0

    try:
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
        await message.reply(f"Successfully deleted {del_total} messages..")
    except Exception as err:
        await message.reply(f"ERR: {err}")


# Kick members
@app.on_message(filters.command(["kick", "dkick"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == 1507530289:
        return await message.reply_text("I can't kick myself, i can leave if you want.")
    if user_id in SUDO:
        return await message.reply_text("Wow, you wanna kick my owner?")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text("Lol, it's crazy if i can kick an admin.")
    mention = (await app.get_users(user_id)).mention
    msg = f"""
**Kicked User:** {mention}
**Kicked By:** {message.from_user.mention if message.from_user else 'Anon'}
**Reason:** {reason or '-'}"""
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    try:
        await message.chat.ban_member(user_id)
        await message.reply_text(msg)
        await asyncio.sleep(1)
        await message.chat.unban_member(user_id)
    except ChatAdminRequired:
        await message.reply("Please give me ban permission to ban user in this group.")


# Ban/DBan/TBan User
@app.on_message(filters.command(["ban", "dban", "tban"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def banFunc(_, message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)

    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == 1507530289:
        return await message.reply_text("I can't ban myself, i can leave if you want.")
    if user_id in SUDO:
        return await message.reply_text("You Wanna Ban The Elevated One?, RECONSIDER!")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text("I can't ban an admin, You know the rules, so do i.")

    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = message.reply_to_message.sender_chat.title if message.reply_to_message else "Anon"

    msg = f"**Banned User:** {mention}\n" f"**Banned By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += f"**Banned For:** {time_value}\n"
        if temp_reason:
            msg += f"**Reason:** {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                await message.reply_text(msg)
            else:
                await message.reply_text("You can't use more than 99")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**Reason:** {reason}"
    keyboard = ikb({"🚨 Unban 🚨": f"unban_{user_id}"})
    await message.chat.ban_member(user_id)
    await message.reply_text(msg, reply_markup=keyboard)


# Unban members
@app.on_message(filters.command("unban", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def unban_func(_, message):
    # we don't need reasons for unban, also, we
    # don't need to get "text_mention" entity, because
    # normal users won't get text_mention if the user
    # they want to unban is not in the group.
    reply = message.reply_to_message

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text("You cannot unban a channel")

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await message.reply_text("Provide a username or reply to a user's message to unban.")
    await message.chat.unban_member(user)
    umention = (await app.get_users(user)).mention
    await message.reply_text(f"Unbanned! {umention}")


# Ban users listed in a message
@app.on_message(filters.user(SUDO) & filters.command("listban", COMMAND_HANDLER) & ~filters.private)
async def list_ban_(c, message):
    userid, msglink_reason = await extract_user_and_reason(message)
    if not userid or not msglink_reason:
        return await message.reply_text("Provide a userid/username along with message link and reason to list-ban")
    if len(msglink_reason.split(" ")) == 1:  # message link included with the reason
        return await message.reply_text("You must provide a reason to list-ban")
    # seperate messge link from reason
    lreason = msglink_reason.split()
    messagelink, reason = lreason[0], " ".join(lreason[1:])

    if not re.search(r"(https?://)?t(elegram)?\.me/\w+/\d+", messagelink):  # validate link
        return await message.reply_text("Invalid message link provided")

    if userid == 1507530289:
        return await message.reply_text("I can't ban myself.")
    if userid in SUDO:
        return await message.reply_text("You Wanna Ban The Elevated One?, RECONSIDER!")
    splitted = messagelink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text("`Banning User from multiple groups. This may take some time`")
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall("@\w+", msgtext)
    except:
        return await m.edit_text("Could not get group usernames")
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

    msg = f"""
**List-Banned User:** {mention}
**Banned User ID:** `{userid}`
**Admin:** {message.from_user.mention}
**Affected chats:** `{count}`
**Reason:** {reason}
"""
    await m.edit_text(msg)


# Unban users listed in a message
@app.on_message(filters.user(SUDO) & filters.command("listunban", COMMAND_HANDLER) & ~filters.private)
async def list_unban_(c, message):
    userid, msglink = await extract_user_and_reason(message)
    if not userid or not msglink:
        return await message.reply_text("Provide a userid/username along with message link to list-unban")

    if not re.search(r"(https?://)?t(elegram)?\.me/\w+/\d+", msglink):  # validate link
        return await message.reply_text("Invalid message link provided")

    splitted = msglink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(
        "`Unbanning User from multiple groups. \
         This may take some time`"
    )
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall("@\w+", msgtext)
    except:
        return await m.edit_text("Could not get the group usernames")
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
    msg = f"""
**List-Unbanned User:** {mention}
**Unbanned User ID:** `{userid}`
**Admin:** {message.from_user.mention}
**Affected chats:** `{count}`
"""
    await m.edit_text(msg)


# Delete messages
@app.on_message(filters.command("del", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_delete_messages")
async def deleteFunc(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply To A Message To Delete It")
    await message.reply_to_message.delete()
    await message.delete()


# Promote Members
@app.on_message(filters.command(["promote", "fullpromote"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_promote_members")
async def promoteFunc(_, message):
    user_id = await extract_user(message)
    umention = (await app.get_users(user_id)).mention
    if not user_id:
        return await message.reply_text("I can't find that user.")
    bot = await app.get_chat_member(message.chat.id, 1507530289)
    if user_id == 1507530289:
        return await message.reply_text("I can't promote myself.")
    if not bot.can_promote_members:
        return await message.reply_text("I don't have enough permissions")
    if message.command[0][0] == "f":
        await message.chat.promote_member(
            user_id=user_id,
            can_change_info=bot.can_change_info,
            can_invite_users=bot.can_invite_users,
            can_delete_messages=bot.can_delete_messages,
            can_restrict_members=bot.can_restrict_members,
            can_pin_messages=bot.can_pin_messages,
            can_promote_members=bot.can_promote_members,
            can_manage_chat=bot.can_manage_chat,
            can_manage_voice_chats=bot.can_manage_voice_chats,
        )
        return await message.reply_text(f"Fully Promoted! {umention}")

    await message.chat.promote_member(
        user_id=user_id,
        can_change_info=False,
        can_invite_users=bot.can_invite_users,
        can_delete_messages=bot.can_delete_messages,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False,
        can_manage_chat=bot.can_manage_chat,
        can_manage_voice_chats=bot.can_manage_voice_chats,
    )
    await message.reply_text(f"Promoted! {umention}")


# Demote Member
@app.on_message(filters.command("demote", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_promote_members")
async def demote(_, message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == 1507530289:
        return await message.reply_text("I can't demote myself.")
    if user_id in SUDO:
        return await message.reply_text("You wanna demote the elevated one?")
    await message.chat.promote_member(
        user_id=user_id,
        can_change_info=False,
        can_invite_users=False,
        can_delete_messages=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False,
        can_manage_chat=False,
        can_manage_voice_chats=False,
    )
    umention = (await app.get_users(user_id)).mention
    await message.reply_text(f"Demoted! {umention}")


# Pin Messages
@app.on_message(filters.command(["pin", "unpin"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_pin_messages")
async def pin(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to pin/unpin it.")
    r = message.reply_to_message
    try:
        if message.command[0][0] == "u":
            await r.unpin()
            return await message.reply_text(
                f"**Unpinned [this]({r.link}) message.**",
                disable_web_page_preview=True,
            )
        await r.pin(disable_notification=True)
        await message.reply(
            f"**Pinned [this]({r.link}) message.**",
            disable_web_page_preview=True,
        )
    except ChatAdminRequired:
        await message.reply(
            "Please give me admin access to use this command.",
            disable_web_page_preview=True,
        )


# Mute members
@app.on_message(filters.command(["mute", "tmute"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def mute(_, message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == 1507530289:
        return await message.reply_text("I can't mute myself.")
    if user_id in SUDO:
        return await message.reply_text("You wanna mute the elevated one?, RECONSIDER!")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text("I can't mute an admin, You know the rules, so do i.")
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨   Unmute   🚨": f"unmute_{user_id}"})
    msg = f"**Muted User:** {mention}\n" f"**Muted By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    if message.command[0] == "tmute":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += f"**Muted For:** {time_value}\n"
        if temp_reason:
            msg += f"**Reason:** {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(),
                    until_date=temp_mute,
                )
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text("You can't use more than 99")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    await message.reply_text(msg, reply_markup=keyboard)


# Unmute members
@app.on_message(filters.command("unmute", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def unmute(_, message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    await message.reply_text(f"Unmuted! {umention}")


# Ban deleted accounts
@app.on_message(filters.command("ban_ghosts", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def ban_deleted_accounts(_, message):
    chat_id = message.chat.id
    deleted_users = []
    m = await message.reply("Finding ghosts...")

    async for i in app.iter_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if deleted_users:
        banned_users = 0
        for deleted_user in deleted_users:
            try:
                await message.chat.ban_member(deleted_user)
            except Exception:
                pass
            banned_users += 1
        await m.edit(f"Banned {banned_users} Deleted Accounts")
    else:
        await m.edit("There are no deleted accounts in this chat")


@app.on_message(filters.command(["warn", "dwarn"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def warn_user(_, message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == 1507530289:
        return await message.reply_text("I can't warn myself, i can leave if you want.")
    if user_id in SUDO:
        return await message.reply_text("You Wanna Warn The Elevated One?, RECONSIDER!")
    if user_id in (await list_admins(chat_id)):
        return await message.reply_text("I can't warn an admin, You know the rules, so do i.")
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({"🚨  Remove Warn  🚨": f"unwarn_{user_id}"})
    warns = warns["warns"] if warns else 0
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(f"Number of warns of {mention} exceeded, BANNED!")
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = f"""
**Warned User:** {mention}
**Warned By:** {message.from_user.mention if message.from_user else 'Anon'}
**Reason:** {reason or 'No Reason Provided.'}
**Warns:** {warns + 1}/3"""
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_"))
async def remove_warning(_, cq):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action.\n" + f"Permission needed: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer("User has no warnings.")
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__Warn removed by {from_user.mention}__"
    await cq.message.edit(text)


@app.on_callback_query(filters.regex("unmute_"))
async def unmute_user(_, cq):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action.\n" + f"Permission needed: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__Mute removed by {from_user.mention}__"
    await cq.message.chat.unban_member(user_id)
    await cq.message.edit(text)


@app.on_callback_query(filters.regex("unban_"))
async def unban_user(_, cq):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action.\n" + f"Permission needed: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    (await app.get_users(user_id)).mention
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__Banned removed by {from_user.mention}__"
    await cq.message.chat.unban_member(user_id)
    await cq.message.edit(text)


# Remove Warn
@app.on_message(filters.command("rmwarn", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to remove a user's warnings.")
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(f"{mention} have no warnings.")
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(f"Removed warnings of {mention}.")


# Warns
@app.on_message(filters.command("warns", COMMAND_HANDLER) & ~filters.private)
@capture_err
async def check_warns(_, message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(f"{mention} has no warnings.")
    return await message.reply_text(f"{mention} has {warns}/3 warnings.")


# Report User in Group
@app.on_message((filters.command("report", COMMAND_HANDLER) | filters.command(["admins", "admin"], prefixes="@")) & ~filters.private)
@capture_err
async def report_user(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to report that user.")
    reply = message.reply_to_message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    if reply_id == user_id:
        return await message.reply_text("Why are you reporting yourself ?")

    list_of_admins = await list_admins(message.chat.id)
    linked_chat = (await app.get_chat(message.chat.id)).linked_chat
    if linked_chat is None:
        if reply_id in list_of_admins or reply_id == message.chat.id:
            return await message.reply_text("Do you know that the user you are replying is an admin ?")

    elif reply_id in list_of_admins or reply_id == message.chat.id or reply_id == linked_chat.id:
        return await message.reply_text("Do you know that the user you are replying is an admin ?")
    user_mention = reply.from_user.mention if reply.from_user else reply.sender_chat.title
    text = f"Reported {user_mention} to admins!"
    admin_data = [m async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)]
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            # return bots or deleted admins
            continue
        text += f"[\u2063](tg://user?id={admin.user.id})"
    await message.reply_to_message.reply_text(text)
