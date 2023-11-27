"""
MIT License

Copyright (c) 2021 TheHamkerCat

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
from re import findall

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.notes_db import delete_note, get_note, get_note_names, save_note, deleteall_notes
from misskaty import app
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.permissions import adminsOnly, member_permissions
from misskaty.core.keyboard import ikb
from misskaty.helper.functions import extract_text_and_keyb, extract_urls


__MODULE__ = "Notes"
__HELP__ = """/notes To Get All The Notes In The Chat.

/save [NOTE_NAME] or /addnote [NOTE_NAME] To Save A Note.

Supported note types are Text, Animation, Photo, Document, Video, video notes, Audio, Voice.

To change caption of any files use.\n/save [NOTE_NAME] or /addnote [NOTE_NAME] [NEW_CAPTION].

#NOTE_NAME To Get A Note.

/delete [NOTE_NAME] or delnote [NOTE_NAME] To Delete A Note.
/deleteall To delete all the notes in a chat (permanently).
"""


@app.on_message(filters.command(["addnote", "save"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_change_info")
async def save_notee(_, message):
    try:
        if len(message.command) < 2 or not message.reply_to_message:
            await message.reply_msg("**Usage:**\nReply to a message with /save [NOTE_NAME] to save a new note.")
        else:
            text = message.text.markdown
            name = text.split(None, 1)[1].strip()
            if not name:
                return await message.reply_msg("**Usage**\n__/save [NOTE_NAME]__")
            replied_message = message.reply_to_message
            text = name.split(" ", 1)
            if len(text) > 1:
                name = text[0]
                data = text[1].strip()
                if replied_message.sticker or replied_message.video_note:
                    data = None
            else:
                if replied_message.sticker or replied_message.video_note:
                    data = None
                elif not replied_message.text and not replied_message.caption:
                    data = None
                else:
                    data = replied_message.text.markdown if replied_message.text else replied_message.caption.markdown
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
            if replied_message.reply_markup and not "~" in data:
                urls = extract_urls(replied_message.reply_markup)
                if urls:
                    response = "\n".join([f"{name}=[{text}, {url}]" for name, text, url in urls])
                    data = data + response
            note = {
                "type": _type,
                "data": data,
                "file_id": file_id,
            }
            prefix = message.text.split()[0][0]
            chat_id = message.chat.id
            await save_note(chat_id, name, note)
            await message.reply_msg(f"__**Saved note {name}.**__")
    except UnboundLocalError:
        return await message.reply_text("**Replied message is inaccessible.\n`Forward the message and try again`**")


@app.on_message(filters.command("notes", COMMAND_HANDLER) & ~filters.private)
@capture_err
async def get_notes(_, message):
    chat_id = message.chat.id
    _notes = await get_note_names(chat_id)

    if not _notes:
        return await message.reply("**No notes in this chat.**")
    _notes.sort()
    msg = f"List of notes in {message.chat.title} - {message.chat.id}\n"
    for note in _notes:
        msg += f"**-** `{note}`\n"
    await message.reply(msg)


@app.on_message(filters.regex(r"^#.+") & filters.text & ~filters.private)
@capture_err
async def get_one_note(self, message):
    name = message.text.replace("#", "", 1)
    if not name:
        return
    _note = await get_note(message.chat.id, name)
    if not _note:
        return
    type_ = _note.get("type")
    data = _note.get("data")
    file_id = _note.get("file_id")
    keyb = None
    if data:       
        if findall(r"\[.+\,.+\]", data):
            keyboard = extract_text_and_keyb(ikb, data)
            if keyboard:
                data, keyb = keyboard
    replied_message = message.reply_to_message
    if replied_message:
        if replied_message.from_user.id != message.from_user.id:
            message = replied_message
    if type_ == "text":
        await message.reply_text(
            text=data,
            reply_markup=keyb,
            disable_web_page_preview=True,
        )
    if type_ == "sticker":
        await message.reply_sticker(
            sticker=file_id,
        )
    if type_ == "animation":
        await message.reply_animation(
            animation=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type_ == "photo":
        await message.reply_photo(
            photo=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type_ == "document":
        await message.reply_document(
            document=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type_ == "video":
        await message.reply_video(
            video=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type_ == "video_note":
        await message.reply_video_note(
            video_note=file_id,
        )
    if type_ == "audio":
        await message.reply_audio(
            audio=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type_ == "voice":
        await message.reply_voice(
            voice=file_id,
            caption=data,
            reply_markup=keyb,
        )


@app.on_message(filters.command(["delnote", "clear"], COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_change_info")
async def del_note(_, message):
    if len(message.command) < 2:
        return await message.reply_msg("**Usage**\n__/delete [NOTE_NAME]__")
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await message.reply_msg("**Usage**\n__/delete [NOTE_NAME]__")

    prefix = message.text.split()[0][0]
    chat_id = message.chat.id

    deleted = await delete_note(chat_id, name)
    if deleted:
        await message.reply_msg(f"**Deleted note {name} successfully.**")
    else:
        await message.reply_msg("**No such note.**")


@app.on_message(filters.command("deleteall", COMMAND_HANDLER) & ~filters.private)
@adminsOnly("can_change_info")
async def delete_all(_, message):
    _notes = await get_note_names(message.chat.id)
    if not _notes:
        return await message.reply_text("**No notes in this chat.**")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("YES, DO IT", callback_data="delete_yes"), 
                 InlineKeyboardButton("Cancel", callback_data="delete_no")
                ]
            ]
        )
        await message.reply_text("**Are you sure you want to delete all the notes in this chat forever ?.**", reply_markup=keyboard)


@app.on_callback_query(filters.regex("delete_(.*)"))
async def delete_all_cb(_, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_change_info"
    if permission not in permissions:
        return await cb.answer(f"You don't have the required permission.\n Permission: {permission}", show_alert=True)
    input = cb.data.split("_", 1)[1]
    if input == "yes":
        stoped_all = await deleteall_notes(chat_id)
        if stoped_all:
            return await cb.message.edit("**Successfully deleted all notes on this chat.**")
