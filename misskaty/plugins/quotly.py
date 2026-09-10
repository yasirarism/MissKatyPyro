from io import BytesIO

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from misskaty import app
from misskaty.helper.http import fetch
from misskaty.vars import BOT_TOKEN


class QuotlyException(Exception):
    pass


async def get_message_sender_id(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return 1
        elif ctx.forward_from:
            return ctx.forward_from.id
        elif ctx.forward_from_chat:
            return ctx.forward_from_chat.id
        else:
            return 1
    elif ctx.from_user:
        return ctx.from_user.id
    elif ctx.sender_chat:
        return ctx.sender_chat.id
    else:
        return 1


async def get_message_sender_name(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return ctx.forward_sender_name
        elif ctx.forward_from:
            return (
                f"{ctx.forward_from.first_name} {ctx.forward_from.last_name}"
                if ctx.forward_from.last_name
                else ctx.forward_from.first_name
            )
        elif ctx.forward_from_chat:
            return ctx.forward_from_chat.title
        else:
            return ""
    elif ctx.from_user:
        if ctx.from_user.last_name:
            return f"{ctx.from_user.first_name} {ctx.from_user.last_name}"
        else:
            return ctx.from_user.first_name
    elif ctx.sender_chat:
        return ctx.sender_chat.title
    else:
        return ""


async def get_custom_emoji(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name or not ctx.forward_from:
            return ""
        if ctx.forward_from and ctx.forward_from.emoji_status:
            return ctx.forward_from.emoji_status.custom_emoji_id or ""
        return ""
    if ctx.from_user and ctx.from_user.emoji_status:
        return ctx.from_user.emoji_status.custom_emoji_id or ""
    return ""


async def get_message_sender_username(ctx: Message):
    if ctx.forward_date:
        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
        ):
            return ctx.forward_from_chat.username or ""
        elif ctx.forward_from:
            return ctx.forward_from.username or ""
        return ""
    elif ctx.from_user and ctx.from_user.username:
        return ctx.from_user.username
    elif ctx.sender_chat and ctx.sender_chat.username:
        return ctx.sender_chat.username
    return ""


async def get_message_sender_photo(ctx: Message):
    if ctx.forward_date:
        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
            and ctx.forward_from_chat.photo
        ):
            return {"big_file_id": ctx.forward_from_chat.photo.big_file_id}
        elif ctx.forward_from and ctx.forward_from.photo:
            return {"big_file_id": ctx.forward_from.photo.big_file_id}
        return ""
    elif ctx.from_user and ctx.from_user.photo:
        return {"big_file_id": ctx.from_user.photo.big_file_id}
    elif ctx.sender_chat and ctx.sender_chat.photo:
        return {"big_file_id": ctx.sender_chat.photo.big_file_id}
    return ""


async def get_admin_title(client: Client, chat_id: int, user_id: int):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if isinstance(member, ChatMemberStatus):
            return ""
        if hasattr(member, "custom_title") and member.custom_title:
            return member.custom_title
        if member.status == ChatMemberStatus.OWNER:
            return "Owner"
    except Exception:
        pass
    return ""


async def get_sender_from(ctx: Message, client: Client = None):
    user = None
    if ctx.forward_date:
        user = ctx.forward_from
    elif ctx.from_user:
        user = ctx.from_user
    if user:
        sender = {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "photo": await get_message_sender_photo(ctx),
            "emoji_status": await get_custom_emoji(ctx) or None,
        }
        if client and ctx.chat and ctx.chat.type.name in ("GROUP", "SUPERGROUP"):
            sender["senderTag"] = await get_admin_title(client, ctx.chat.id, user.id) or None
        return sender
    if ctx.forward_from_chat:
        chat = ctx.forward_from_chat
        return {
            "id": chat.id,
            "first_name": chat.title or "",
            "last_name": "",
            "username": chat.username or "",
            "photo": await get_message_sender_photo(ctx),
        }
    if ctx.sender_chat:
        chat = ctx.sender_chat
        return {
            "id": chat.id,
            "first_name": chat.title or "",
            "last_name": "",
            "username": chat.username or "",
            "photo": await get_message_sender_photo(ctx),
        }
    return {"id": 1, "first_name": "Unknown", "last_name": "", "username": ""}


def build_entities(msg: Message):
    ents = msg.entities or msg.caption_entities or []
    result = []
    for e in ents:
        ent = {
            "type": e.type.name.lower(),
            "offset": e.offset,
            "length": e.length,
        }
        if e.type.name == "TEXT_LINK":
            ent["url"] = e.url
        elif e.type.name == "TEXT_MENTION":
            ent["user"] = {"id": e.user.id}
        elif e.type.name == "CUSTOM_EMOJI":
            ent["custom_emoji_id"] = str(e.custom_emoji_id)
        result.append(ent)
    return result


async def get_text_or_caption(ctx: Message):
    if ctx.text:
        return ctx.text
    elif ctx.caption:
        return ctx.caption
    return ""


async def pyrogram_to_quotly(client, messages, is_reply):
    if not isinstance(messages, list):
        messages = [messages]
    payload = {
        "botToken": BOT_TOKEN,
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [],
    }

    for message in messages:
        msg_dict = {
            "text": await get_text_or_caption(message),
            "entities": build_entities(message),
            "avatar": True,
            "from": await get_sender_from(message, client),
        }
        if message.reply_to_message and is_reply:
            reply_from = await get_sender_from(message.reply_to_message, client)
            msg_dict["replyMessage"] = {
                "name": await get_message_sender_name(message.reply_to_message),
                "text": await get_text_or_caption(message.reply_to_message),
                "chatId": await get_message_sender_id(message.reply_to_message),
                "from": reply_from,
                "entities": build_entities(message.reply_to_message),
            }
        else:
            msg_dict["replyMessage"] = {}
        payload["messages"].append(msg_dict)

    r = await fetch.post("https://quote-api.yasirweb.eu.org/generate.png", json=payload)
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


@app.on_message(filters.command(["q", "qr"]) & filters.reply)
async def msg_quotly_cmd(self: Client, ctx: Message):
    is_reply = bool(ctx.command[0].endswith("r"))
    if len(ctx.text.split()) > 1:
        check_arg = isArgInt(ctx.command[1])
        if check_arg[0]:
            if check_arg[1] < 2 or check_arg[1] > 10:
                return await ctx.reply("Invalid range", del_in=6)
            try:
                messages = [
                    i
                    for i in await self.get_messages(
                        chat_id=ctx.chat.id,
                        message_ids=range(
                            ctx.reply_to_message.id,
                            ctx.reply_to_message.id + (check_arg[1] + 5),
                        ),
                        replies=-1,
                    )
                    if not i.empty and not i.media
                ]
            except Exception:
                return await ctx.reply_text("🤷🏻♂️")
            try:
                make_quotly = await pyrogram_to_quotly(self, messages, is_reply=is_reply)
                bio_sticker = BytesIO(make_quotly)
                bio_sticker.name = "misskatyquote_sticker.webp"
                return await ctx.reply_sticker(bio_sticker)
            except Exception:
                return await ctx.reply("🤷🏻♂️")
    try:
        messages_one = await self.get_messages(
            chat_id=ctx.chat.id, message_ids=ctx.reply_to_message.id, replies=-1
        )
        messages = [messages_one]
    except Exception:
        return await ctx.reply("🤷🏻♂️")
    try:
        make_quotly = await pyrogram_to_quotly(self, messages, is_reply=is_reply)
        bio_sticker = BytesIO(make_quotly)
        bio_sticker.name = "misskatyquote_sticker.webp"
        return await ctx.reply_sticker(bio_sticker)
    except Exception as e:
        return await ctx.reply(f"ERROR: {e}")
