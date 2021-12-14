import re

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message
from database import db, dbc

dbc.execute(
    """
CREATE TABLE IF NOT EXISTS notes(
    chat_id INTEGER ,
    note_name,
    raw_data,
    file_id,
    note_type
)
    """
)


def add_note(chat_id, trigger, raw_data, file_id, note_type):
    dbc.execute(
        "INSERT INTO notes(chat_id, note_name, raw_data, file_id, note_type) VALUES(?, ?, ?, ?, ?)",
        (chat_id, trigger, raw_data, file_id, note_type),
    )
    db.commit()


def update_note(chat_id, trigger, raw_data, file_id, note_type):
    dbc.execute(
        "UPDATE notes SET raw_data = ?, file_id = ?, note_type = ? WHERE chat_id = ? AND note_name = ?",
        (raw_data, file_id, note_type, chat_id, trigger),
    )
    db.commit()


def rm_note(chat_id, trigger):
    dbc.execute(
        "DELETE from notes WHERE chat_id = ? AND note_name = ?", (chat_id, trigger)
    )
    db.commit()


def get_all_notes(chat_id):
    dbc.execute("SELECT * FROM notes WHERE chat_id = ?", (chat_id,))

    return dbc.fetchall()


def check_for_notes(chat_id, trigger):
    all_notes = get_all_notes(chat_id)
    for keywords in all_notes:
        keyword = keywords[1]
        if trigger == keyword:
            return True
    return False

@Client.on_message(filters.command(["note", "savenote"], "!"))
async def save_note(c: Client, m: Message, strings):
    args = m.text.html.split(maxsplit=1)
    split_text = split_quotes(args[1])
    trigger = split_text[0].lower()

    if m.reply_to_message is None and len(split_text) < 2:
        await m.reply_text("add_note_empty", quote=True)
        return

    if m.reply_to_message and m.reply_to_message.photo:
        file_id = m.reply_to_message.photo.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "photo"
    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "document"
    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "video"
    elif m.reply_to_message and m.reply_to_message.audio:
        file_id = m.reply_to_message.audio.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "audio"
    elif m.reply_to_message and m.reply_to_message.animation:
        file_id = m.reply_to_message.animation.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "animation"
    elif m.reply_to_message and m.reply_to_message.sticker:
        file_id = m.reply_to_message.sticker.file_id
        raw_data = split_text[1] if len(split_text) > 1 else None
        note_type = "sticker"
    else:
        file_id = None
        raw_data = split_text[1]
        note_type = "text"

    chat_id = m.chat.id
    check_note = check_for_notes(chat_id, trigger)
    if check_note:
        update_note(chat_id, trigger, raw_data, file_id, note_type)
    else:
        add_note(chat_id, trigger, raw_data, file_id, note_type)
    await m.reply_text(f"add_note_success {trigger}", quote=True)

@Client.on_message(filters.command(["delnote", "rmnote"], "!"))
async def delete_note(c: Client, m: Message, strings):
    args = m.text.html.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_note = check_for_notes(chat_id, trigger)
    if check_note:
        rm_note(chat_id, trigger)
        await m.reply_text(f"remove_note_success {trigger}", quote=True
        )
    else:
        await m.reply_text(f"no_note_with_name {trigger}",quote=True)

@Client.on_message(filters.command("notes", "!"))
async def get_all_chat_note(c: Client, m: Message, strings):
    chat_id = m.chat.id
    reply_text = strings("notes_list")
    all_notes = get_all_notes(chat_id)
    for note_s in all_notes:
        keyword = note_s[1]
        reply_text += f" - {keyword} \n"

    if not all_notes:
        await m.reply_text("notes_list_empty", quote=True)
    else:
        await m.reply_text(reply_text, quote=True)
