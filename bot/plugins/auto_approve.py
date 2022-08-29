from bot import app
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


@app.on_chat_join_request(filters.chat(-1001686184174))
async def approve_join_chat(c: Client, m: ChatJoinRequest):
    if not m.from_user:
        return
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="Sudah/Already", callback_data=f"approve_{m.chat.id}"), InlineKeyboardButton(text="Belum/Not Yet", callback_data=f"declined_{m.chat.id}")]])
    await c.send_message(
        m.from_user.id,
        "<b>PERMINTAAN JOIN CHANNEL YMOVIEZ REBORN</b>\n\nID: Sebelum masuk ke channel, apakah anda sudah membaca catatan di https://t.me/YMovieZ_New/4 ? Jika sudah silahkan klik <b>Sudah</b> ..\n\nEN: Have you read the notes in https://t.me/YMovieZ_New/4 ? If so, please click <b>Already</b>",
        disable_web_page_preview=True,
        reply_markup=markup,
    )


@app.on_callback_query(filters.regex(r"^approve"))
async def approve_chat(c: Client, q: CallbackQuery):
    i, chat = q.data.split("_")
    await q.message.edit(f"Yeayy, selamat kamu bisa bergabung di Channel YMovieZ Reborn. Jangan lupa share yakk biar makin banyak subnya..")
    await c.approve_chat_join_request(chat, q.from_user.id)


@app.on_callback_query(filters.regex(r"^declined"))
async def decline_chat(c: Client, q: CallbackQuery):
    i, chat = q.data.split("_")
    await q.message.edit("Yahh, sayang banget kamu ga jadi subs ke channel ini karena menekan tombol tolak..")
    await c.decline_chat_join_request(chat, q.from_user.id)


# Todo: Add exception if bot blocked
