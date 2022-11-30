import time
from asyncio import sleep
from misskaty import app
from info import COMMAND_HANDLER
from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserAdminInvalid

__MODULE__ = "Inkick"
__HELP__ = """"
/instatus - View member status in group.
/dkick - Remove deleted account from group.
"""


@app.on_message(filters.incoming & ~filters.private & filters.command(["inkick"], COMMAND_HANDLER))
async def inkick(_, message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ("administrator", "owner"):
        if len(message.command) > 1:
            input_str = message.command
            sent_message = await message.reply_text("🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**")
            count = 0
            async for member in app.get_chat_members(message.chat.id):
                if member.user.is_bot:
                    continue
                if member.user.status.value in input_str and not member.status.value in ("administrator", "owner"):
                    try:
                        await message.chat.ban_member(member.user.id)
                        count += 1
                        await sleep(1)
                        await message.chat.unban_member(member.user.id)
                    except (ChatAdminRequired, UserAdminInvalid):
                        await sent_message.edit("❗**Oh tidaakk, saya bukan admin disini**\n__Saya pergi dari sini, tambahkan aku kembali dengan perijinan banned pengguna.__")
                        await app.leave_chat(message.chat.id)
                        break
                    except FloodWait as e:
                        await sleep(e.value)
            try:
                await sent_message.edit("✔️ **Berhasil menendang {} pengguna berdasarkan argumen.**".format(count))
            except ChatWriteForbidden:
                await app.leave_chat(message.chat.id)
        else:
            await message.reply_text("❗ **Arguments Required**\n__See /help in personal message for more information.__")
    else:
        sent_message = await message.reply_text("❗ **You have to be the group creator to do that.**")
        await sleep(5)
        await sent_message.delete()


# Kick User Without Username
@app.on_message(filters.incoming & ~filters.private & filters.command(["uname"], COMMAND_HANDLER))
async def uname(_, message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ("administrator", "owner"):
        sent_message = await message.reply_text("🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**")
        count = 0
        async for member in app.get_chat_members(message.chat.id):
            if not member.user.username and not member.status.value in ("administrator", "owner"):
                try:
                    await message.chat.ban_member(member.user.id)
                    count += 1
                    await sleep(1)
                    await message.chat.unban_member(member.user.id)
                except (ChatAdminRequired, UserAdminInvalid):
                    await sent_message.edit("❗**Oh tidaakk, saya bukan admin disini**\n__Saya pergi dari sini, tambahkan aku kembali dengan perijinan banned pengguna.__")
                    await app.leave_chat(message.chat.id)
                    break
                except FloodWait as e:
                    await sleep(e.value)
        try:
            await sent_message.edit("✔️ **Berhasil menendang {} pengguna berdasarkan argumen.**".format(count))
        except ChatWriteForbidden:
            await app.leave_chat(message.chat.id)
    else:
        sent_message = await message.reply_text("❗ **You have to be the group creator to do that.**")
        await sleep(5)
        await sent_message.delete()


@app.on_message(filters.incoming & ~filters.private & filters.command(["dkick"], COMMAND_HANDLER))
async def dkick(client, message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ("administrator", "owner"):
        sent_message = await message.reply_text("🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**")
        count = 0
        async for member in app.get_chat_members(message.chat.id):
            if member.user.is_deleted and not member.status.value in ("administrator", "owner"):
                try:
                    await message.chat.ban_member(member.user.id)
                    count += 1
                    await sleep(1)
                    await message.chat.unban_member(member.user.id)
                except (ChatAdminRequired, UserAdminInvalid):
                    await sent_message.edit("❗**Oh tidaakk, saya bukan admin disini**\n__Saya pergi dari sini, tambahkan aku kembali dengan perijinan banned pengguna.__")
                    await app.leave_chat(message.chat.id)
                    break
                except FloodWait as e:
                    await sleep(e.value)
        try:
            await sent_message.edit("✔️ **Berhasil menendang {} akun terhapus.**".format(count))
        except ChatWriteForbidden:
            await app.leave_chat(message.chat.id)
    else:
        sent_message = await message.reply_text("❗ **Kamu harus jadi admin atau owner grup untuk melakukan tindakan ini.**")
        await sleep(5)
        await sent_message.delete()


@app.on_message(filters.incoming & ~filters.private & filters.command(["instatus"], COMMAND_HANDLER))
async def instatus(client, message):
    start_time = time.perf_counter()
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    count = await app.get_chat_members_count(message.chat.id)
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        sent_message = await message.reply_text("**Sedang mengumpulkan informasi pengguna...**")
        recently = 0
        within_week = 0
        within_month = 0
        long_time_ago = 0
        deleted_acc = 0
        premium_acc = 0
        no_username = 0
        restricted = 0
        banned = 0
        uncached = 0
        bot = 0
        async for ban in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BANNED):
            banned += 1
        async for restr in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
            restricted += 1
        async for member in app.get_chat_members(message.chat.id):
            user = member.user
            if user.is_deleted:
                deleted_acc += 1
            elif user.is_bot:
                bot += 1
            elif user.is_premium:
                premium_acc += 1
            elif not user.username:
                no_username += 1
            elif user.status.value == "recently":
                recently += 1
            elif user.status.value == "last_week":
                within_week += 1
            elif user.status.value == "last_month":
                within_month += 1
            elif user.status.value == "long_ago":
                long_time_ago += 1
            else:
                uncached += 1
        end_time = time.perf_counter()
        timelog = "{:.2f}".format(end_time - start_time)
        await sent_message.edit(
            "<b>💠 {}\n👥 {} Anggota\n——————\n👁‍🗨 Informasi Status Anggota\n——————\n</b>🕒 <code>recently</code>: {}\n🕒 <code>last_week</code>: {}\n🕒 <code>last_month</code>: {}\n🕒 <code>long_ago</code>: {}\n🉑 Tanpa Username: {}\n🤐 Dibatasi: {}\n🚫 Diblokir: {}\n👻 Deleted Account (<code>/dkick</code>): {}\n🤖 Bot: {}\n⭐️ Premium User: {}\n👽 UnCached: {}\n\n⏱ Waktu eksekusi {} detik.".format(
                message.chat.title, count, recently, within_week, within_month, long_time_ago, no_username, restricted, banned, deleted_acc, bot, premium_acc, uncached, timelog
            )
        )
    else:
        sent_message = await message.reply_text("❗ **Kamu harus jadi admin atau owner grup untuk melakukan tindakan ini.**")
        await sleep(5)
        await sent_message.delete()
