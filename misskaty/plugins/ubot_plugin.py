"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
# Code in this plugin to learn basic userbot in pyrogram
import os
from datetime import datetime

from pyrogram import enums, filters
from pyrogram.raw import functions
from pyrogram.types import (
    ChatEventFilter,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from misskaty import app, user

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


@user.on_deleted_messages(filters.chat([-1001455886928, -1001255283935]))
async def del_msg(_, message):
    async for a in user.get_chat_event_log(
        message[0].chat.id, limit=1, filters=ChatEventFilter(deleted_messages=True)
    ):
        try:
            ustat = (
                await user.get_chat_member(
                    message[0].chat.id, a.deleted_message.from_user.id
                )
            ).status
        except:
            ustat = enums.ChatMemberStatus.MEMBER
        if (
            ustat
            in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            or a.deleted_message.from_user.is_bot
        ):
            return
        if a.user.id == a.deleted_message.from_user.id:
            if a.deleted_message.text:
                await app.send_message(
                    a.deleted_message.chat.id,
                    f"#DELETED_MESSAGE\n\n<a href='tg://user?id={a.deleted_message.from_user.id}'>{a.deleted_message.from_user.first_name}</a> menghapus pesannya 🧐.\n<b>Pesan:</b> {a.deleted_message.text}",
                )
            elif a.deleted_message.video:
                await app.send_message(
                    a.deleted_message.chat.id,
                    f"#DELETED_MESSAGE\n\n<a href='tg://user?id={a.deleted_message.from_user.id}'>{a.deleted_message.from_user.first_name}</a> menghapus pesannya 🧐.\n<b>Nama file:</b> {a.deleted_message.video.file_name}",
                )


@user.on_edited_message(filters.text & filters.chat(-1001455886928))
async def edit_msg(_, message):
    try:
        ustat = (
            await user.get_chat_member(message.chat.id, message.from_user.id)
        ).status
    except:
        ustat = enums.ChatMemberStatus.MEMBER
    if message.from_user.is_bot or ustat in [
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ]:
        return
    async for a in user.get_chat_event_log(
        message.chat.id, limit=1, filters=ChatEventFilter(edited_messages=True)
    ):
        if a.old_message.text.startswith(
            ("/mirror", "/leech", "/unzipmirror", "/unzipleech")
        ):
            await app.send_message(
                message.chat.id,
                f"#EDITED_MESSAGE\n\n<a href='tg://user?id={a.user.id}'>{a.user.first_name}</a> mengedit pesannya 🧐.\n<b>Pesan:</b> {a.old_message.text}",
            )


@user.on_message(filters.private & ~filters.bot & ~filters.me & filters.text)
async def message_pm(_, message):
    await app.send_message(
        617426792,
        f"Ada pesan baru dari {message.from_user.mention}\n\n<b>Pesan: </b>{message.text}",
    )


@user.on_message(~filters.bot & filters.group & filters.mentioned)
async def mentioned(_, message):
    if message.sender_chat:
        return
    cid = message.chat.id
    pesan = message.text or message.caption
    await app.send_message(
        617426792,
        f"{message.from_user.mention} mention kamu di {message.chat.title}\n\n<b>Pesan:</b> {pesan}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="💬 Lihat Pesan",
                        url=f"https://t.me/c/{str(cid)[4:]}/{message.id}",
                    )
                ]
            ]
        ),
    )


@user.on_message(filters.command("joindate", "!") & filters.me)
async def join_date(self, message: Message):
    members = []
    async for m in self.iter_chat_members(message.chat.id):
        members.append(
            (
                m.user.first_name,
                m.joined_date or (await self.get_messages(message.chat.id, 1)).date,
            )
        )
    members.sort(key=lambda member: member[1])

    with open("joined_date.txt", "w", encoding="utf8") as fj:
        fj.write("Join Date      First Name\n")
        for member in members:
            fj.write(
                str(datetime.fromtimestamp(member[1]).strftime("%y-%m-%d %H:%M"))
                + f" {member[0]}\n"
            )

    await user.send_document(message.chat.id, "joined_date.txt")
    os.remove("joined_date.txt")


@user.on_message(filters.command("memberstats", "!") & filters.me)
async def memberstats(_, message):
    people = {}
    total = await user.get_chat_members_count(message.chat.id)
    async for msg in user.iter_history(message.chat.id, limit=1000):
        if msg.from_user and not msg.from_user.is_bot:
            people[msg.from_user.id] = msg.from_user.first_name
    await message.edit(f"{round(len(people) / total)}%")


@user.on_message(filters.command("recent_action", "!") & filters.me)
async def recent_act(_, message):
    full_log = await user.invoke(
        functions.channels.GetAdminLog(
            channel=await user.resolve_peer(message.chat.id),
            q="",
            max_id=0,
            min_id=0,
            limit=0,
        )
    )
    with open(
        f"recent_actions_{message.chat.id}.txt", "w", encoding="utf8"
    ) as log_file:
        log_file.write(str(full_log))
    await message.reply_document(f"recent_actions_{message.chat.id}.txt")


@user.on_message(filters.command(["screenshot"], prefixes="!"))
async def take_a_screenshot(_, message):
    await message.delete()
    await user.invoke(
        functions.messages.SendScreenshotNotification(
            peer=await user.resolve_peer(message.chat.id),
            reply_to_msg_id=0,
            random_id=app.rnd_id(),
        )
    )
