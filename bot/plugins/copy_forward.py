from pyrogram import filters, Client
from pyrogram.errors import PeerIdInvalid
from info import COMMAND_HANDLER

@Client.on_message(filters.command(["copy","copy@MissKatyRoBot"], COMMAND_HANDLER))
async def copy(client, message):
    try:
        to = message.text.split(" ")[1]
        reply = message.reply_to_message
        user = await client.get_chat_member(-1001404537486, message.from_user.id)
        if user.status in ['administrator','creator']:
           if not reply and not to:
              return await message.reply_text("Silahkan balas pesan yang mau dicopy, lalu kirim command /copy [chat_tujuan]")
           await client.copy_message(to, message.chat.id, message.reply_to_message.message_id, reply_markup=message.reply_to_message.reply_markup)
           await message.reply_text("Pesan berhasil dikirim..")
        else:
           await message.reply_text("😝😝😝")
    except Exception as e:
        await message.reply_text(e)

@Client.on_message(filters.command(["forward","forward@MissKatyRoBot"], COMMAND_HANDLER))
async def forward(client, message):
    try:
        to = message.text.split(" ")[1]
        reply = message.reply_to_message
        user = await client.get_chat_member(-1001404537486, message.from_user.id)
        if user.status in ['administrator','creator']:
           if not reply and not to:
              return await message.reply_text("Silahkan balas pesan yang mau diforward, lalu kirim command /forward [chat_tujuan]")
           await client.forward_messages(to, message.chat.id, message.reply_to_message.message_id)
           await message.reply_text("Pesan berhasil dikirim..")
        else:
           await message.reply_text("😝😝😝")
    except Exception as e:
        await message.reply_text(e)
