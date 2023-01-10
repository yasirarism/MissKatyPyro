from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.users_chats_db import db
from misskaty import app
from misskaty.vars import SUPPORT_CHAT
from utils import temp


async def banned_users(_, client, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS


banned_user = filters.create(banned_users)


async def disabled_chat(_, client, message: Message):
    return message.chat.id in temp.BANNED_CHATS


disabled_group = filters.create(disabled_chat)


@app.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    ban = await db.get_ban_status(message.from_user.id)
    await message.reply(
        f'Sorry Dude, You are Banned to use Me. \nBan Reason: {ban["ban_reason"]}'
    )


@app.on_message(filters.group & disabled_group & filters.incoming)
async def grp_bd(bot, message):
    buttons = [[InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}")]]
    reply_markup = InlineKeyboardMarkup(buttons)
    vazha = await db.get_chat(message.chat.id)
    k = await message.reply(
        text=f"CHAT NOT ALLOWED 🐞\n\nMy admins has restricted me from working here ! If you want to know more about it contact support..\nReason : <code>{vazha['reason']}</code>.",
        reply_markup=reply_markup,
    )
    try:
        await k.pin()
    except:
        pass
    await bot.leave_chat(message.chat.id)
