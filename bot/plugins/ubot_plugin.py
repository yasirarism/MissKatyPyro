import os, re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatEventFilter
)
from pyrogram.handlers import MessageHandler
from pyrogram.raw import functions, types
from typing import List
from bot import user, app
from datetime import datetime

f = filters.chat([])
AFK = []

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

@user.on_message(filters.command('afk', "!") & filters.me)
async def afk(client, message):
    start = datetime.now().replace(microsecond=0)
    if len(message.text.split()) >= 2:
        reason = message.text.split(" ", maxsplit=1)[1]
    else:
        reason = "Randue alesan.."
    AFK.append([start, reason])
    await app.send_message(message.chat.id, "<b>Byee @YasirArisM, kamu sekarang di mode AFK.. </b>")

@user.on_message(filters.command('unafk', "!") & filters.me)
async def unafk(client, message):
    try:
        await app.send_message(message.chat.id, f"<b>Kamu sudah tidak AFK lagi yakk.. ")
        AFK.clear()
    except:
        AFK.clear()
        pass

@user.on_deleted_messages(filters.chat([-1001455886928, -1001255283935]))
async def del_msg(client, message):
    async for a in user.get_chat_event_log(message[0].chat.id, limit=1, filters=ChatEventFilter(deleted_messages=True)):
       try:
          pengguna = await user.get_chat_member(message[0].chat.id, a.deleted_message.from_user.id).status
       except:
          pass
       if pengguna.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or pengguna.user.is_bot:
          return
       if a.user.id == a.deleted_message.from_user.id:
          if a.deleted_message.text:
             await app.send_message(a.deleted_message.chat.id, f"#DELETED_MESSAGE\n\n<a href='tg://user?id={a.deleted_message.from_user.id}'>{a.deleted_message.from_user.first_name}</a> menghapus pesannya 🧐.\n<b>Pesan:</b> {a.deleted_message.text}")
          elif a.deleted_message.video:
             await app.send_message(a.deleted_message.chat.id, f"#DELETED_MESSAGE\n\n<a href='tg://user?id={a.deleted_message.from_user.id}'>{a.deleted_message.from_user.first_name}</a> menghapus pesannya 🧐.\n<b>Nama file:</b> {a.deleted_message.video.file_name}")

@user.on_edited_message(filters.chat([-1001455886928, -1001255283935]) & filters.regex(r"^(/leech|/mirror), re.I"))
async def edit_msg(client, message):
    edit_log = await user.send(
        functions.channels.GetAdminLog(
            channel= await user.resolve_peer(message[0].chat.id),
            q="",
            max_id=0,
            min_id=0,
            limit=1,
            events_filter=types.ChannelAdminLogEventsFilter(edit=True),
        )
    )
    try:
        pengguna = await user.get_chat_member(message[0].chat.id, edit_log.users[0].id).status
    except:
        pass
    if edit_log.users[0].bot or pengguna.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return
    await app.send_message(message[0].chat.id, f"#EDITED_MESSAGE\n\n<a href='tg://user?id={edit_log.users[0].id}'>{edit_log.users[0].first_name}</a> mengedit pesannya 🧐.\n<b>Pesan:</b> {edit_log.events[0].action.message.message}")
    
@user.on_message(filters.private & ~filters.bot & ~filters.me)
async def message_pm(client, message):
    await app.send_message(617426792, f"Ada pesan baru dari {message.from_user.mention}")

@user.on_message(~filters.bot & filters.group & filters.mentioned)
async def mentioned(client, message):
    cid = message.chat.id
    pesan = message.text or message.caption
    await app.send_message(617426792, f"{message.from_user.mention} mention kamu di {message.chat.title}\n\n<b>Pesan:</b> {pesan}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 Lihat Pesan", url=f"https://t.me/c/{str(cid)[4:]}/{message.id}")]]))
    if AFK:
        end = datetime.now().replace(microsecond=0)
        afk_time = (end - AFK[0][0])
        alasan = AFK[0][1]
        try:
            await app.send_message(message.chat.id, f"<b>⚠️ Mohon maaf {message.from_user.mention}, Owner saya sedang AFK selama {afk_time}</b>..\n<b>Alasan:</b> <code>{alasan}</code>", reply_to_message_id=message.id)
        except:
            pass

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
    await message.edit(f'{round(len(people) / total)}%')

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
