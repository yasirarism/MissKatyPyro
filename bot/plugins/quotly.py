from pyrogram import Client, filters
from pyrogram.types import Message

from bot import app
from bot.helper.http import http
from io import BytesIO

__MODULE__ = "Fun"
__HELP__ = """
/q [int] - Generate quotly from message
/memify [text] - Reply to sticker to give text on sticker.
"""

class QuotlyException(Exception):
    pass


async def get_message_sender_id(m: Message):
    if m.forward_date:
        if m.forward_sender_name:
            return 1
        elif m.forward_from:
            return m.forward_from.id
        elif m.forward_from_chat:
            return m.forward_from_chat.id
        else:
            return 1
    else:
        if m.from_user:
            return m.from_user.id
        elif m.sender_chat:
            return m.sender_chat.id
        else:
            return 1


async def get_message_sender_name(m: Message):
    if m.forward_date:
        if m.forward_sender_name:
            return m.forward_sender_name
        elif m.forward_from:
            if m.forward_from.last_name:
                return f"{m.forward_from.first_name} {m.forward_from.last_name}"
            else:
                return m.forward_from.first_name
        elif m.forward_from_chat:
            return m.forward_from_chat.title
        else:
            return ""
    else:
        if m.from_user:
            if m.from_user.last_name:
                return f"{m.from_user.first_name} {m.from_user.last_name}"
            else:
                return m.from_user.first_name
        elif m.sender_chat:
            return m.sender_chat.title
        else:
            return ""


async def get_message_sender_username(m: Message):
    if m.forward_date:
        if m.forward_sender_name:
            return ""
        elif m.forward_from:
            if m.forward_from.username:
                return m.forward_from.username
            else:
                return ""
        elif m.forward_from_chat:
            if m.forward_from_chat.username:
                return m.forward_from_chat.username
            else:
                return ""
        else:
            return ""
    else:
        if m.from_user:
            if m.from_user.username:
                return m.from_user.username
            else:
                return ""
        elif m.sender_chat:
            if m.sender_chat.username:
                return m.sender_chat.username
            else:
                return ""
        else:
            return ""


async def get_message_sender_photo(m: Message):
    if m.forward_date:
        if m.forward_sender_name:
            return ""
        elif m.forward_from:
            if m.forward_from.photo:
                return {
                    "small_file_id": m.forward_from.photo.small_file_id,
                    "small_photo_unique_id": m.forward_from.photo.small_photo_unique_id,
                    "big_file_id": m.forward_from.photo.big_file_id,
                    "big_photo_unique_id": m.forward_from.photo.big_photo_unique_id,
                }
            else:
                return ""
        elif m.forward_from_chat:
            if m.forward_from_chat.photo:
                return {
                    "small_file_id": m.forward_from_chat.photo.small_file_id,
                    "small_photo_unique_id": m.forward_from_chat.photo.small_photo_unique_id,
                    "big_file_id": m.forward_from_chat.photo.big_file_id,
                    "big_photo_unique_id": m.forward_from_chat.photo.big_photo_unique_id,
                }
            else:
                return ""
        else:
            return ""
    else:
        if m.from_user:
            if m.from_user.photo:
                return {
                    "small_file_id": m.from_user.photo.small_file_id,
                    "small_photo_unique_id": m.from_user.photo.small_photo_unique_id,
                    "big_file_id": m.from_user.photo.big_file_id,
                    "big_photo_unique_id": m.from_user.photo.big_photo_unique_id,
                }
            else:
                return ""
        elif m.sender_chat:
            if m.sender_chat.photo:
                return {
                    "small_file_id": m.sender_chat.photo.small_file_id,
                    "small_photo_unique_id": m.sender_chat.photo.small_photo_unique_id,
                    "big_file_id": m.sender_chat.photo.big_file_id,
                    "big_photo_unique_id": m.sender_chat.photo.big_photo_unique_id,
                }
            else:
                return ""
        else:
            return ""


async def get_text_or_caption(m: Message):
    if m.text:
        return m.text
    elif m.caption:
        return m.caption
    else:
        return ""


async def pyrogram_to_quotly(messages):
    if not isinstance(messages, list):
        messages = [messages]
    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [],
    }

    for message in messages:
        the_message_dict_to_append = {}
        if message.entities:
            the_message_dict_to_append["entities"] = [
                {
                    "type": entity.type.name.lower(),
                    "offset": entity.offset,
                    "length": entity.length,
                }
                for entity in message.entities
            ]
        elif message.caption_entities:
            the_message_dict_to_append["entities"] = [
                {
                    "type": entity.type.name.lower(),
                    "offset": entity.offset,
                    "length": entity.length,
                }
                for entity in message.caption_entities
            ]
        else:
            the_message_dict_to_append["entities"] = []
        the_message_dict_to_append["chatId"] = await get_message_sender_id(message)
        the_message_dict_to_append["text"] = await get_text_or_caption(message)
        the_message_dict_to_append["avatar"] = True
        the_message_dict_to_append["from"] = {}
        the_message_dict_to_append["from"]["id"] = await get_message_sender_id(message)
        the_message_dict_to_append["from"]["name"] = await get_message_sender_name(message)
        the_message_dict_to_append["from"]["username"] = await get_message_sender_username(message)
        the_message_dict_to_append["from"]["type"] = message.chat.type.name.lower()
        the_message_dict_to_append["from"]["photo"] = await get_message_sender_photo(message)
        if message.reply_to_message:
            the_message_dict_to_append["replyMessage"] = {
                "name": await get_message_sender_name(message.reply_to_message),
                "text": await get_text_or_caption(message.reply_to_message),
                "chatId": await get_message_sender_id(message.reply_to_message),
            }
        else:
            the_message_dict_to_append["replyMessage"] = {}
        payload["messages"].append(the_message_dict_to_append)
    r = await http.post(f"https://bot.lyo.su/quote/generate.png", json=payload)
    if not r.is_error:
        return r.read()
    else:
        raise QuotlyException(r.json())


def isArgInt(txt) -> list:
    count = txt
    try:
        count = int(count)
        return [True, count]
    except ValueError:
        return [False, 0]


@app.on_message(filters.command(["q"]) & filters.reply)
async def msg_quotly_cmd(c: Client, m: Message):
    if len(m.text.split()) > 1:
        check_arg = isArgInt(m.command[1])
        if check_arg[0]:
            if check_arg[1] < 2 or check_arg[1] > 10:
                return await m.reply_text("Invalid range")
            else:
                try:
                    messages = [
                        i
                        for i in await c.get_messages(
                            chat_id=m.chat.id,
                            message_ids=range(
                                m.reply_to_message.id,
                                m.reply_to_message.id + (check_arg[1] + 5),
                            ),
                            replies=-1,
                        )
                        if not i.empty and not i.media
                    ]
                except Exception:
                    return await m.reply_text(f"🤷🏻‍♂️")
                try:
                    make_quotly = await pyrogram_to_quotly(messages)
                    bio_sticker = BytesIO(make_quotly)
                    bio_sticker.name = "biosticker.webp"
                    return await m.reply_sticker(bio_sticker)
                except Exception:
                    return await m.reply_text(f"🤷🏻‍♂️")
        else:
            pass
    try:
        messages_one = await c.get_messages(chat_id=m.chat.id, message_ids=m.reply_to_message.id, replies=-1)
        messages = [messages_one]
    except Exception:
        return await m.reply_text(f"🤷🏻‍♂️")
    try:
        make_quotly = await pyrogram_to_quotly(messages)
        bio_sticker = BytesIO(make_quotly)
        bio_sticker.name = "biosticker.webp"
        return await m.reply_sticker(bio_sticker)
    except Exception as e:
        return await m.reply_text(f"ERROR: {e}")
