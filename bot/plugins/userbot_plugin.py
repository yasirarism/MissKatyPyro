import os
from pyrogram import Client, filters
from pyrogram.types import (
    Message
)
from pyrogram.raw import functions
from typing import List
from bot import user, app

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

@user.on_deleted_messages(filters.chat(-1001455886928))
async def del_msg(client, message):
    await app.send_message(617426792, message)

@user.on_message(filters.private & ~filters.bot & ~filters.me)
async def message_pm(client, message):
    await app.forward_messages(617426792, message.chat.id, message.message_id)

@user.on_message(~filters.bot & filters.group & filters.mentioned)
async def mentioned(client, message):
    pesan = message.text if message.text else message.caption
    await app.send_message(617426792, f"{message.from_user.mention} mention kamu di {message.chat.title}\n\nPesan: {pesan}")

@user.on_message(filters.command("joindate", "!") & filters.me)
async def join_date(app, message: Message):
    members = []
    for m in user.iter_chat_members(message.chat.id):
        members.append(
            (
                m.user.first_name,
                m.joined_date or app.get_messages(message.chat.id, 1).date,
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
    total = await user.get_chat_members_count(chat)
    for msg in await user.iter_history(chat, limit=1000):
        if msg.from_user and not msg.from_user.is_bot:
            people[msg.from_user.id] = msg.from_user.first_name
    await message.edit(len(people) / total)

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
    with open(f"recent_actions_{chat}.txt", "w", encoding="utf8") as log_file:
       log_file.write(str(full_log))
    await message.reply_document(full_log)

@user.on_message(filters.command(["screenshot"], prefixes="!"))
async def take_a_screenshot(app, message):
    await message.delete()
    await user.send(
        functions.messages.SendScreenshotNotification(
            peer=await user.resolve_peer(message.chat.id),
            reply_to_msg_id=0,
            random_id=app.rnd_id(),
        )
    )
