import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatEventFilter
)
from pyrogram.handlers import MessageHandler
from pyrogram.raw import functions, types
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

async def afk_handler(client, message):
    try:
        global start, end
        end = datetime.now().replace(microsecond=0)
        afk_time = (end - start)
        if message.from_user.is_bot is False:
            await message.reply_text(f"<b>Saya AFK sejak {afk_time}</b>\n"
                                     f"<b>Alasan:</b> <i>{reason}</i>")
    except NameError:
        pass

@user.on_message(filters.command('afk', "!") & filters.me)
async def afk(client, message):
    global start, end, handler, reason
    start = datetime.now().replace(microsecond=0)
    handler = await user.add_handler(MessageHandler(afk_handler, (~filters.me & filters.mentioned)))
    if len(message.text.split()) >= 2:
        reason = message.text.split(" ", maxsplit=1)[1]
    else:
        reason = "Tidak ada alasan.."
    await message.edit("<b>I'm going afk</b>")

@user.on_message(filters.command('unafk', "!") & filters.me)
async def unafk(client, message):
    try:
        global start, end
        end = datetime.now().replace(microsecond=0)
        afk_time = (end - start)
        await message.edit(f"<b>Saya tidak AFK lagi.\nSaya telah AFK selama {afk_time}</b>")
        client.remove_handler(*handler)
    except NameError:
        await message.edit("<b>Kamu kan tidak afk</b>")
        await asyncio.sleep(3)
        await message.delete()

@user.on_deleted_messages(filters.chat([-1001455886928, -1001255283935]))
async def del_msg(client, message):
    async for a in user.get_chat_event_log(message[0].chat.id, limit=1, filters=ChatEventFilter(deleted_messages=True)):
       if a.user.id == a.deleted_message.from_user.id:
          if a.deleted_message.text:
             await app.send_message(a.deleted_message.chat.id, f"#DELETED_MESSAGE\n\n<a href='tg://user?id={a.deleted_message.from_user.id}'>{a.deleted_message.from_user.first_name}</a> menghapus pesannya 🧐.\n<b>Pesan:</b> {a.deleted_message.text}")
          elif a.deleted_message.video:
             await app.send_message(a.deleted_message.chat.id, f"#DELETED_MESSAGE\n\n<a href='tg://user?id={a.deleted_message.from_user.id}'>{a.deleted_message.from_user.first_name}</a> menghapus pesannya 🧐.\n<b>Nama file:</b> {a.deleted_message.video.file_name}")
   # users = await user.get_chat_member(message[0].chat.id, del_log.users[0].id)
   # if del_log.users[0].bot or users.status in ['administrator','creator']:
   #    return

@user.on_deleted_messages(filters.chat([-1001455886928, -1001255283935]))
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
    users = await user.get_chat_member(message[0].chat.id, edit_log.users[0].id)
    if edit_log.users[0].bot or users.status in ['administrator','creator']:
        return
    if edit_log.events[0].action.message.message.startswith('/mirror') or edit_log.events[0].action.message.message.startswith('/leech'):
        await app.send_message(message[0].chat.id, f"#EDITED_MESSAGE\n\n<a href='tg://user?id={edit_log.users[0].id}'>{edit_log.users[0].first_name}</a> mengedit pesannya 🧐.\n<b>Pesan:</b> {edit_log.events[0].action.message.message}")
    
@user.on_message(filters.private & ~filters.bot & ~filters.me)
async def message_pm(client, message):
    await app.send_message(617426792, f"Ada pesan baru dari {message.from_user.mention}")

@user.on_message(~filters.bot & filters.group & filters.mentioned)
async def mentioned(client, message):
    cid = message.chat.id
    pesan = message.text if message.text else message.caption
    await app.send_message(617426792, f"{message.from_user.mention} mention kamu di {message.chat.title}\n\n<b>Pesan:</b> {pesan}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 Lihat Pesan", url=f"https://t.me/c/{str(cid)[4:]}/{message.message_id}")]]))

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
