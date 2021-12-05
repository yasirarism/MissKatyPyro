import os
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.raw import functions
from typing import List
from bot import user, app
from datetime import datetime

f = filters.chat([])

@user.on_message(f)
async def auto_read(_, message: Message):
    await user.read_history(message.chat.id)
    await message.continue_propagation()

@user.on_message(filters.command("autoscroll", "!") & filters.me)
async def add_keep(_, message: Message):
    if message.chat.id in f:
        f.remove(message.chat.id)
        await message.edit("Autoscroll dimatikan")
    else:
        f.add(message.chat.id)
        await message.edit("Autoscroll diaktifkan, semua chat akan otomatis terbaca")

@user.on_deleted_messages(filters.chat(-1001455886928) & ~filters.bot)
async def del_msg(client, message):
    await app.send_message(617426792, message)

@user.on_message(filters.private & ~filters.bot & ~filters.me)
async def message_pm(client, message):
    await app.send_message(617426792, f"Ada pesan baru dari {message.from_user.mention}")

@user.on_message(~filters.bot & filters.group & filters.mentioned)
async def mentioned(client, message):
    pesan = message.text if message.text else message.caption
    await app.send_message(617426792, f"{message.from_user.mention} mention kamu di {message.chat.title}\n\nPesan: {pesan}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 Lihat Pesan", url=f"https://t.me/c/{message.chat.id[-3:]}/{message.message_id}")]]))

@user.on_message(filters.command("joindate", "!") & filters.me)
async def join_date(app, message: Message):
    members = []
    async for m in app.iter_chat_members(message.chat.id):
        members.append(
            (
                m.user.first_name,
                m.joined_date or (await app.get_messages(message.chat.id, 1)).date,
            )
        )
    members.sort(key=lambda member: member[1])

    with open("joined_date.txt", "w", encoding="utf8") as f:
        f.write("Join Date      First Name\n")
        for member in members:
            f.write(
                str(datetime.fromtimestamp(member[1]).strftime("%y-%m-%d %H:%M"))
                + f" {member[0]}\n"
            )

    await user.send_document(message.chat.id, "joined_date.txt")
    os.remove("joined_date.txt")

@user.on_message(filters.command("memberstats", "!") & filters.me)
async def memberstats(client, message):
    people = {}
    total = await user.get_chat_members_count(message.chat.id)
    async for msg in user.iter_history(message.chat.id, limit=1000):
        if msg.from_user and not msg.from_user.is_bot:
            people[msg.from_user.id] = msg.from_user.first_name
    await message.edit(round(len(people) / total)+"%")

@user.on_message(filters.command("recent_action", "!") & filters.me)
async def recent_act(client, message):
    full_log = await user.send(
        functions.channels.GetAdminLog(
            channel= await user.resolve_peer(message.chat.id),
            q="",
            max_id=0,
            min_id=0,
            limit=0,
        )
    )
    with open(f"recent_actions_{message.chat.id}.txt", "w", encoding="utf8") as log_file:
       log_file.write(str(full_log))
    await message.reply_document(f"recent_actions_{message.chat.id}.txt")

@user.on_message(filters.command(["screenshot"], prefixes="!"))
async def take_a_screenshot(client, message):
    await message.delete()
    await user.send(
        functions.messages.SendScreenshotNotification(
            peer=await user.resolve_peer(message.chat.id),
            reply_to_msg_id=0,
            random_id=app.rnd_id(),
        )
    )
