
from pyrogram import filters
from pyrogram import types as pyro_types
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.notes_db import (
    delete_note,
    deleteall_notes,
    get_note,
    get_note_names,
    save_note,
)
from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.permissions import member_permissions
from misskaty.core.keyboard import ikb
from misskaty.helper.functions import apply_fillings, extract_text_and_keyb, extract_urls, has_button_markup
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "Notes"
__HELP__ = """/notes To Get All The Notes In The Chat.

/save [NOTE_NAME] or /addnote [NOTE_NAME] To Save A Note.

Supported note types are Text, Animation, Photo, Document, Video, video notes, Audio, Voice.

To change caption of any files use.\n/save [NOTE_NAME] or /addnote [NOTE_NAME] [NEW_CAPTION].

#NOTE_NAME To Get A Note.

/delete [NOTE_NAME] or delnote [NOTE_NAME] To Delete A Note.
/deleteall To delete all the notes in a chat (permanently).
Formatting & Button Samples:
- *bold* _italic_ __underline__ ~strike~ ||spoiler||
- `inline code` and:
```shell
echo "hello"
```
- URL button: `[Open](buttonurl://https://example.com)`
- Same row button:
`[One](buttonurl://https://example.com)`
`[Two](buttonurl://https://example.com:same)`
- Note deep-link button: `[Open Note](buttonurl://#notename)`

Tip: save a note by replying text/media, then use #notename to call it.

Fillings

Supported fillings:
- {first}: The user's first name.
- {last}: The user's last name.
- {fullname}: The user's full name.
- {username}: The user's username. If they don't have one, mentions the user instead.
- {mention}: Mentions the user with their firstname.
- {id}: The user's ID.
- {chatname}: The chat's name.
- {rules}: Create a button to the chat's rules on a new row of buttons.
- {rules:same}: Create a button to the chat's rules, on the same row as the previous buttons
- {preview}: Enables link previews for this message.
- {preview:top}: Shows the link preview for this message ABOVE the message text.
- {nonotif}: Disables the notification for this message.
- {protect}: Stop this message from being forwarded, or screenshotted.
- {mediaspoiler}: Marks the message photo/video/animation as being a spoiler.

"""


async def can_manage_notes(message):
    if message.chat.type == ChatType.PRIVATE:
        return True
    if not message.from_user:
        return False
    permissions = await member_permissions(message.chat.id, message.from_user.id)
    return "can_change_info" in permissions


@app.on_message(filters.command(["addnote", "save"], COMMAND_HANDLER))
async def save_notee(_, message):
    if not await can_manage_notes(message):
        return await message.reply("You don't have required permission: can_change_info")
    try:
        if len(message.command) < 2 or not message.reply_to_message:
            await message.reply(
                "**Usage:**\nReply to a message with /save [NOTE_NAME] to save a new note."
            )
        else:
            text = message.text.markdown
            name = text.split(None, 1)[1].strip()
            if not name:
                return await message.reply("**Usage**\n__/save [NOTE_NAME]__")
            replied_message = message.reply_to_message
            text = name.split(" ", 1)
            if len(text) > 1:
                name = text[0]
                data = text[1].strip()
                if replied_message.sticker or replied_message.video_note:
                    data = None
            elif replied_message.sticker or replied_message.video_note:
                data = None
            elif not replied_message.text and not replied_message.caption:
                data = None
            else:
                data = (
                    replied_message.text.markdown
                    if replied_message.text
                    else replied_message.caption.markdown
                )
            if replied_message.text:
                _type = "text"
                file_id = None
            if replied_message.sticker:
                _type = "sticker"
                file_id = replied_message.sticker.file_id
            if replied_message.animation:
                _type = "animation"
                file_id = replied_message.animation.file_id
            if replied_message.photo:
                _type = "photo"
                file_id = replied_message.photo.file_id
            if replied_message.document:
                _type = "document"
                file_id = replied_message.document.file_id
            if replied_message.video:
                _type = "video"
                file_id = replied_message.video.file_id
            if replied_message.video_note:
                _type = "video_note"
                file_id = replied_message.video_note.file_id
            if replied_message.audio:
                _type = "audio"
                file_id = replied_message.audio.file_id
            if replied_message.voice:
                _type = "voice"
                file_id = replied_message.voice.file_id
            if replied_message.reply_markup and not has_button_markup(data):
                if urls := extract_urls(replied_message.reply_markup):
                    response = "\n".join(
                        [f"{name}=[{text}, {url}]" for name, text, url in urls]
                    )
                    data = data + response
            note = {
                "type": _type,
                "data": data,
                "file_id": file_id,
            }
            prefix = message.text.split()[0][0]
            chat_id = message.chat.id
            await save_note(chat_id, name, note)
            await message.reply(f"__**Saved note {name}.**__")
    except UnboundLocalError:
        return await message.reply_text(
            "**Replied message is inaccessible.\n`Forward the message and try again`**"
        )


@app.on_message(filters.command("notes", COMMAND_HANDLER))
@capture_err
async def get_notes(_, message):
    chat_id = message.chat.id
    _notes = await get_note_names(chat_id)

    if not _notes:
        return await message.reply("**No notes in this chat.**")
    _notes.sort()
    chat_name = message.chat.title or message.chat.first_name
    msg = f"List of notes in {chat_name} - {message.chat.id}\n"
    for note in _notes:
        msg += f"**-** `{note}`\n"
    await message.reply(msg)


@app.on_message(filters.regex(r"^#.+") & filters.text)
@capture_err
async def get_one_note(_, message):
    from_user = message.from_user if message.from_user else message.sender_chat
    chat_id = message.chat.id
    name = message.text.replace("#", "", 1)
    if not name:
        return
    note = await get_note(chat_id, name)
    if not note:
        return
    return await send_note_message(message, note, from_user, chat_id)


async def send_note_message(message, note: dict, from_user, source_chat_id: int):
    type = note.get("type")
    data = note.get("data")
    file_id = note.get("file_id")
    keyb = None

    if data:
        if has_button_markup(data):
            keyboard = extract_text_and_keyb(ikb, data, chat_id=source_chat_id)
            if keyboard:
                data, keyb = keyboard
        data, keyb, send_opts = await apply_fillings(data, message, from_user, keyb)
    else:
        send_opts = {"disable_notification": False, "protect_content": False, "media_spoiler": False, "preview": False, "preview_top": False}

    replied_message = message.reply_to_message
    if replied_message:
        replied_user = replied_message.from_user if replied_message.from_user else replied_message.sender_chat
        if replied_user and replied_user.id != from_user.id:
            message = replied_message

    if type == "text":
        return await message.reply_text(
            text=data,
            reply_markup=keyb,
            link_preview_options=pyro_types.LinkPreviewOptions(
                is_disabled=not send_opts["preview"],
                show_above_text=send_opts["preview_top"],
            ),
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
        )
    if type == "sticker":
        return await message.reply_sticker(
            sticker=file_id,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
        )
    if type == "animation":
        return await message.reply_animation(
            animation=file_id,
            caption=data,
            reply_markup=keyb,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
            has_spoiler=send_opts["media_spoiler"],
        )
    if type == "photo":
        return await message.reply_photo(
            photo=file_id,
            caption=data,
            reply_markup=keyb,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
            has_spoiler=send_opts["media_spoiler"],
        )
    if type == "document":
        return await message.reply_document(
            document=file_id,
            caption=data,
            reply_markup=keyb,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
        )
    if type == "video":
        return await message.reply_video(
            video=file_id,
            caption=data,
            reply_markup=keyb,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
            has_spoiler=send_opts["media_spoiler"],
        )
    if type == "video_note":
        return await message.reply_video_note(
            video_note=file_id,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
        )
    if type == "audio":
        return await message.reply_audio(
            audio=file_id,
            caption=data,
            reply_markup=keyb,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
        )
    if type == "voice":
        return await message.reply_voice(
            voice=file_id,
            caption=data,
            reply_markup=keyb,
            disable_notification=send_opts["disable_notification"],
            protect_content=send_opts["protect_content"],
        )


@app.on_message(filters.private & filters.command("start") & filters.regex(r"^/start btnnotesm_"))
@capture_err
async def get_private_note(_, message):
    if len(message.command) < 2:
        return
    payload = message.command[1]
    if not payload.startswith("btnnotesm_"):
        return
    try:
        _, chat_id, name = payload.split("_", 2)
        chat_id = int(chat_id)
    except Exception:
        return await message.reply("Invalid note button payload.")

    note = await get_note(chat_id, name)
    if not note:
        return await message.reply("Note not found.")

    return await send_note_message(message, note, message.from_user, chat_id)


@app.on_message(filters.command(["delnote", "clear"], COMMAND_HANDLER))
async def del_note(_, message):
    if not await can_manage_notes(message):
        return await message.reply("You don't have required permission: can_change_info")
    if len(message.command) < 2:
        return await message.reply("**Usage**\n__/delete [NOTE_NAME]__")
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await message.reply("**Usage**\n__/delete [NOTE_NAME]__")

    prefix = message.text.split()[0][0]
    chat_id = message.chat.id

    deleted = await delete_note(chat_id, name)
    if deleted:
        await message.reply(f"**Deleted note {name} successfully.**")
    else:
        await message.reply("**No such note.**")


@app.on_message(filters.command("deleteall", COMMAND_HANDLER))
async def delete_all(_, message):
    if not await can_manage_notes(message):
        return await message.reply("You don't have required permission: can_change_info")
    _notes = await get_note_names(message.chat.id)
    if not _notes:
        return await message.reply_text("**No notes in this chat.**")
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("YES, DO IT", callback_data="delete_yes"),
                InlineKeyboardButton("Cancel", callback_data="delete_no"),
            ]
        ]
    )
    await message.reply_text(
        "**Are you sure you want to delete all the notes in this chat forever ?.**",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("delete_(.*)"))
async def delete_all_cb(_, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    if cb.message.chat.type != ChatType.PRIVATE:
        permissions = await member_permissions(chat_id, from_user.id)
        permission = "can_change_info"
        if permission not in permissions:
            return await cb.answer(
                f"You don't have the required permission.\n Permission: {permission}",
                show_alert=True,
            )
    input = cb.data.split("_", 1)[1]
    if input == "yes":
        stoped_all = await deleteall_notes(chat_id)
        if stoped_all:
            return await cb.message.edit(
                "**Successfully deleted all notes on this chat.**"
            )
