import re
import random
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

chat = [-1001128045651, -1001255283935, -1001455886928]

@Client.on_message(filters.regex(r"alamu'?ala[iy]ku+m", re.I) & filters.chat(chat) & ~filters.edited)
async def start(_, message):
    await message.reply_text(
        text=f"Wa'alaikumsalam {message.from_user.mention}"
)
    
@Client.on_message(filters.regex(r"makasi|thank|terimakasih|terima kasih|mksh", re.I) & filters.chat(chat) & ~filters.edited)
async def start(_, message):
    pesan = [f"Sama-sama {message.from_user.first_name}",
             f"You're Welcome {message.from_user.first_name}",
             "Oke..",
             "Terimakasih Kembali..",
             "Sami-Sami...",
             "Sama-sama, senang bisa membantu..",
             f"Yups, Sama-sama {message.from_user.first_name}",
             "Okayyy..."
            ]
    await message.reply_text(text=random.choice(pesan))

@Client.on_message(filters.regex(r"#request|#req", re.I) & (filters.text | filters.photo) & filters.chat(-1001255283935) & ~filters.edited)
async def request_user(client, message):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 Lihat Pesan", url=f"https://t.me/c/1255283935/{message.message_id}")],
                                   [InlineKeyboardButton(text="🚫 Tolak", callback_data=f"rejectreq_{message.message_id}_{message.chat.id}"),InlineKeyboardButton(text="✅ Done", callback_data=f"donereq_{message.message_id}_{message.chat.id}")],
                                   [InlineKeyboardButton(text="⚠️ Tidak Tersedia", callback_data=f"unavailablereq_{message.message_id}_{message.chat.id}")]
                                 ])
    try:
      if message.text:
        forward = await client.send_message(-1001575525902, f"Request by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n\n{message.text}", reply_markup=markup)
        markup2 = InlineKeyboardMarkup([[InlineKeyboardButton(text="⏳ Cek status request", url=f"https://t.me/c/1575525902/{forward.message_id}")]])
      if message.photo:
        forward = await client.send_photo(-1001575525902, message.photo.file_id, caption=f"Request by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n\n{message.caption}", reply_markup=markup)
        markup2 = InlineKeyboardMarkup([[InlineKeyboardButton(text="⏳ Cek status request", url=f"https://t.me/c/1575525902/{forward.message_id}")]])
      await message.reply_text(text=f"Request kamu sudah dikirim yaa. Harap bersabar, mungkin admin juga punya kesibukan lain.", quote=True, reply_markup=markup2)
    except:
      pass

@Client.on_callback_query(filters.regex(r"^donereq"))
async def _callbackreq(c: Client, q: CallbackQuery):
    user = await c.get_chat_member(-1001404537486, q.from_user.id)
    if user.status in ['administrator','creator']:
       i, msg_id, chat_id = q.data.split('_')
       await c.send_message(chat_id=chat_id, text=f"#Done\nDone ✅, pastikan join channel dan grup yaahh untuk melihat request-an nya.", reply_to_message_id=int(msg_id))
       if q.message.caption:
          await q.message.edit_text(f"<b>COMPLETED</b>\n\n<s>{q.message.caption}</s>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="✅ Request Completed", callback_data="reqcompl")]]))
       else:
          await q.message.edit_text(f"<b>COMPLETED</b>\n\n<s>{q.message.text}</s>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="✅ Request Completed", callback_data="reqcompl")]]))
       await q.answer("Request berhasil diselesaikan ✅")
    else:
       await q.answer("😝😝😝", show_alert=True)

@Client.on_callback_query(filters.regex(r"^rejectreq"))
async def _callbackreject(c: Client, q: CallbackQuery):
    user = await c.get_chat_member(-1001404537486, q.from_user.id)
    if user.status in ['administrator','creator']:
       i, msg_id, chat_id = q.data.split('_')
       await c.send_message(chat_id=chat_id, text=f"#Rejected\nMohon maaf, request kamu ditolak karena tidak sesuai rules. Harap baca rules nya dulu yaa 🙃.", reply_to_message_id=int(msg_id))
       if q.message.caption:
          await q.message.edit_text(f"<b>REJECTED</b>\n\n<s>{q.message.caption}</s>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🚫 Request Rejected", callback_data="reqreject")]]))
       else:
          await q.message.edit_text(f"<b>REJECTED</b>\n\n<s>{q.message.text}</s>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🚫 Request Rejected", callback_data="reqreject")]]))
       await q.answer("Requests berhasil ditolak 🚫")
    else:
       await q.answer("😝😝😝", show_alert=True)

@Client.on_callback_query(filters.regex(r"^unavailablereq"))
async def _callbackunav(c: Client, q: CallbackQuery):
    user = await c.get_chat_member(-1001404537486, q.from_user.id)
    if user.status in ['administrator','creator']:
       i, msg_id, chat_id = q.data.split('_')
       await c.send_message(chat_id=chat_id, text=f"#Unavailable\nMohon maaf, request kamu tidak tersedia 😕..", reply_to_message_id=int(msg_id))
       if q.message.caption:
          await q.message.edit_text(f"<b>UNAVAILABLE</b>\n\n<s>{q.message.caption}</s>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="⚠️ Request Unavailable", callback_data="requnav")]]))
       else:
          await q.message.edit_text(f"<b>UNAVAILABLE</b>\n\n<s>{q.message.text}</s>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="⚠️ Request Unavailable", callback_data="requnav")]]))
       await q.answer("Request tidak tersedia.")
    else:
       await q.answer("😝😝😝", show_alert=True)

@Client.on_callback_query(filters.regex(r"^reqcompl$"))
async def _callbackaft_done(c: Client, q: CallbackQuery):
      await q.answer("Request ini sudah tersedia 🥳, silahkan cek di channel atau grup yaa..", show_alert=True)

@Client.on_callback_query(filters.regex(r"^reqreject$"))
async def _callbackaft_rej(c: Client, q: CallbackQuery):
      await q.answer("Request ini ditolak 💔, silahkan cek rules grup yaa. Jika belum paham bisa tanya ke admin lain digrup.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^requnav$"))
async def _callbackaft_unav(c: Client, q: CallbackQuery):
      await q.answer("Request ini tidak tersedia 🥳, mungkin filmnya belum rilis atau memang tidak tersedia versi digital.", show_alert=True)
