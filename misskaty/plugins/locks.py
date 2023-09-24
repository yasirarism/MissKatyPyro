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
from logging import getLogger

from pyrogram import filters
from pyrogram.errors import ChatAdminRequired, ChatNotModified, FloodWait
from pyrogram.types import ChatPermissions

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.permissions import adminsOnly, list_admins
from misskaty.helper.functions import get_urls_from_text
from misskaty.vars import COMMAND_HANDLER, SUDO

LOGGER = getLogger("MissKaty")

__MODULE__ = "Locks"
__HELP__ = """
Commands: /lock | /unlock | /locks [No Parameters Required]

Parameters:
    messages | sticker | gif | media | games | polls

    inline  | url | group_info | user_add | pin | photo

    voice | video | audio | docs | plain

You can only pass the "all" parameter with /lock, not with /unlock

Example:
    /lock all
"""
incorrect_parameters = "Incorrect Parameters, Check Locks Section In Help."
# Using disable_preview as a switch for url checker
# That way we won't need an additional db to check
# If url lock is enabled/disabled for a chat
data = {
    "messages": "can_send_messages",
    "sticker": "can_send_stickers",
    "gif": "can_send_gifs",
    "media": "can_send_media_messages",
    "games": "can_send_games",
    "inline": "can_send_inline",
    "photo": "can_send_photos",
    "video": "can_send_videos",
    "docs": "can_send_docs",
    "voice": "can_send_voices",
    "audio": "can_send_audios",
    "plain": "can_send_plain",
    "url": "can_add_web_page_previews",
    "polls": "can_send_polls",
    "group_info": "can_change_info",
    "useradd": "can_invite_users",
    "pin": "can_pin_messages",
}


async def current_chat_permissions(chat_id):
    perms = []
    try:
        perm = (await app.get_chat(chat_id)).permissions
    except FloodWait as e:
        await asyncio.sleep(e.value)
        perm = (await app.get_chat(chat_id)).permissions
    if perm.can_send_messages:
        perms.append("can_send_messages")
    if perm.can_send_media_messages:
        perms.append("can_send_media_messages")
    if perm.can_send_audios:
        perms.append("can_send_audios")
    if perm.can_send_docs:
        perms.append("can_send_docs")
    if perm.can_send_games:
        perms.append("can_send_games")
    if perm.can_send_gifs:
        perms.append("can_send_gifs")
    if perm.can_send_inline:
        perms.append("can_send_inline")
    if perm.can_send_photos:
        perms.append("can_send_photos")
    if perm.can_send_plain:
        perms.append("can_send_plain")
    if perm.can_send_roundvideos:
        perms.append("can_send_roundvideos")
    if perm.can_send_stickers:
        perms.append("can_send_stickers")
    if perm.can_send_videos:
        perms.append("can_send_videos")
    if perm.can_send_voices:
        perms.append("can_send_voices")
    if perm.can_add_web_page_previews:
        perms.append("can_add_web_page_previews")
    if perm.can_send_polls:
        perms.append("can_send_polls")
    if perm.can_change_info:
        perms.append("can_change_info")
    if perm.can_invite_users:
        perms.append("can_invite_users")
    if perm.can_pin_messages:
        perms.append("can_pin_messages")

    return perms


async def tg_lock(message, permissions: list, perm: str, lock: bool):
    if lock:
        if perm not in permissions:
            return await message.reply_text("Already locked.")
        permissions.remove(perm)
    elif perm in permissions:
        return await message.reply_text("Already Unlocked.")
    else:
        permissions.append(perm)

    permissions = {perm: True for perm in list(set(permissions))}

    try:
        await app.set_chat_permissions(message.chat.id, ChatPermissions(**permissions))
    except ChatNotModified:
        return await message.reply_text(
            "To unlock this, you have to unlock 'messages' first."
        )

    await message.reply_text(("Locked." if lock else "Unlocked."))


@app.on_message(filters.command(["lock", "unlock"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_restrict_members")
async def locks_func(_, message):
    if len(message.command) != 2:
        return await message.reply_msg(incorrect_parameters)

    chat_id = message.chat.id
    parameter = message.text.strip().split(None, 1)[1].lower()
    state = message.command[0].lower()

    if parameter not in data and parameter != "all":
        return await message.reply_text(incorrect_parameters)

    permissions = await current_chat_permissions(chat_id)

    if parameter in data:
        await tg_lock(message, permissions, data[parameter], state == "lock")
    elif parameter == "all" and state == "lock":
        try:
            await app.set_chat_permissions(chat_id, ChatPermissions())
            await message.reply_text(f"Locked Everything in {message.chat.title}")
        except ChatAdminRequired:
            await message.reply_msg(
                "Give me proper admin permission to use this command."
            )

    elif parameter == "all" and state == "unlock":
        try:
            await app.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_plain=True,
                    can_send_media_messages=True,
                    can_send_docs=True,
                    can_send_inline=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_roundvideos=True,
                    can_send_audios=True,
                    can_send_voices=True,
                    can_send_stickers=True,
                    can_send_gifs=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False,
                ),
            )
            await message.reply(f"Unlocked Everything in {message.chat.title}")
        except ChatAdminRequired:
            await message.reply_msg(
                "Give me full admin permission to use this command."
            )


@app.on_message(filters.command("locks", COMMAND_HANDLER) & ~filters.private)
@capture_err
async def locktypes(_, message):
    permissions = await current_chat_permissions(message.chat.id)

    if not permissions:
        return await message.reply_text("No Permissions.")

    perms = "".join(f"__**{i}**__\n" for i in permissions)
    await message.reply_text(perms)


@app.on_message(filters.text & filters.group, group=69)
async def url_detector(_, message):
    user = message.from_user or message.sender_chat
    chat_id = message.chat.id
    text = message.text.lower().strip()

    if not text or not user:
        return
    mods = await list_admins(chat_id)
    if user.id in mods or user.id in SUDO:
        return

    if get_urls_from_text(text):
        permissions = await current_chat_permissions(chat_id)
        if "can_add_web_page_previews" not in permissions:
            try:
                await message.delete_msg()
            except Exception:
                await message.reply_msg(
                    "This message contains a URL, "
                    + "but i don't have enough permissions to delete it"
                )
