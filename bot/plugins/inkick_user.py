import logging
from asyncio import sleep
from bot import app, COMMAND_HANDLER
from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserAdminInvalid

@app.on_message(filters.incoming & ~filters.private & filters.command(['inkick'], COMMAND_HANDLER))
async def inkick(_, message):
  user = await app.get_chat_member(message.chat.id, message.from_user.id)
  if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
    if len(message.command) > 1:
      input_str = message.command
      sent_message = message.reply_text("🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**")
      count = 0
      async for member in app.get_chat_members(message.chat.id):
        if member.user.status in input_str and not member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
          try:
            await app.ban_chat_member(message.chat.id, member.user.id, int(time() + 45))
            count += 1
            await sleep(1)
          except (ChatAdminRequired, UserAdminInvalid):
            await sent_message.edit("❗**Oh tidaakk, saya bukan admin disini**\n__Saya pergi dari sini, tambahkan aku kembali dengan perijinan banned pengguna.__")
            await app.leave_chat(message.chat.id)
            break
          except FloodWait as e:
            await sleep(e.value)
      try:
        await sent_message.edit("✔️ **Berhasil menendang {} pengguna berdasarkan argumen.**".format(count))
      except ChatWriteForbidden:
        pass
    else:
      await message.reply_text("❗ **Arguments Required**\n__See /inkickhelp in personal message for more information.__")
  else:
    sent_message = await message.reply_text("❗ **You have to be the group creator to do that.**")
    await sleep(5)
    await sent_message.delete()

@app.on_message(filters.incoming & ~filters.private & filters.command(['dkick'], COMMAND_HANDLER))
async def dkick(client, message):
  user = await app.get_chat_member(message.chat.id, message.from_user.id)
  if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
    sent_message = message.reply_text("🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**")
    count = 0
    async for member in client.iter_chat_members(message.chat.id):
      if member.user.is_deleted and not member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        try:
          await app.ban_chat_member(message.chat.id, member.user.id, int(time() + 45))
          count += 1
          await sleep(1)
        except (ChatAdminRequired, UserAdminInvalid):
          await sent_message.edit("❗**Oh tidaakk, saya bukan admin disini**\n__Saya pergi dari sini, tambahkan aku kembali dengan perijinan banned pengguna.__")
          await app.leave_chat(message.chat.id)
          break
        except FloodWait as e:
          await sleep(e.value)
    try:
      await sent_message.edit("✔️ **Berhasil menendang {} akun terhapus.**".format(count))
    except ChatWriteForbidden:
      pass
  else:
    sent_message = await message.reply_text("❗ **You have to be the group creator to do that.**")
    await sleep(5)
    await sent_message.delete()
    
@app.on_message(filters.incoming & ~filters.private & filters.command(['instatus'], COMMAND_HANDLER))
async def instatus(client, message):
  user = await app.get_chat_member(message.chat.id, message.from_user.id)
  if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
    sent_message = await message.reply_text("**Sedang mengumpulkan informasi pengguna...**")
    recently = 0
    within_week = 0
    within_month = 0
    long_time_ago = 0
    deleted_acc = 0
    uncached = 0
    bot = 0
    async for member in app.get_chat_members(message.chat.id):
      logging.info(member)
      user = member.user
      if user.is_deleted:
        deleted_acc += 1
      elif user.is_bot:
        bot += 1
      elif user.status == "recently":
        recently += 1
      elif user.status == "within_week":
        within_week += 1
      elif user.status == "within_month":
        within_month += 1
      elif user.status == "long_time_ago":
        long_time_ago += 1
      else:
        uncached += 1
    await sent_message.edit("**{}\nChat Member Status**\n\n```recently``` - {}\n```within_week``` - {}\n```within_month``` - {}\n```long_time_ago``` - {}\nDeleted Account - {}\nBot - {}\nUnCached - {}".format(message.chat.title, recently, within_week, within_month, long_time_ago, deleted_acc, bot, uncached))
