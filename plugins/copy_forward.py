from pyrogram import filters, Client
from pyrogram.errors import PeerIdInvalid
from info import COMMAND_HANDLER

@Client.on_message(filters.command(["copy","copy@MissKatyRoBot"], COMMAND_HANDLER))
async def copy(_, message):
    try:
        to = message.text.split(" ")[1]
        reply = message.reply_to_message
        if not reply and not to:
          return await message.reply_text("Silahkan balas pesan yang mau dicopy, lalu kirim command /copy [chat_tujuan]")
        await client.copy_message(to, message.chat.id, message.reply_to_message.message_id, reply_markup=message.reply_to_message.reply_markup)
        await message.reply_text("Pesan berhasil dikirim..")
    except Exception as e:
        await message.reply_text(e)

@Client.on_message(filters.command(["forward","forward@MissKatyRoBot"], COMMAND_HANDLER))
async def copy(_, message):
    try:
        to = message.text.split(" ")[1]
        reply = message.reply_to_message
        if not reply and not to:
          return await message.reply_text("Silahkan balas pesan yang mau diforward, lalu kirim command /copy [chat_tujuan]")
        await client.forward_messages(to, message.chat.id, message.reply_to_message.message_id)
        await message.reply_text("Pesan berhasil dikirim..")
    except Exception as e:
        await message.reply_text(e)
