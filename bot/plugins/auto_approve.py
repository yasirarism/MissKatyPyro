from bot import app
from pyrogram import filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserIsBlocked
from bot.core.decorator.errors import capture_err

@capture_err
@app.on_chat_join_request(filters.chat(-1001686184174))
async def approve_join_chat(c, m):
    # try:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="Sudah", callback_data=f"approve_{m.chat.id}"), InlineKeyboardButton(text="Belum/Not Yet", callback_data=f"declined_{m.chat.id}")]])
        await c.send_message(
            m.from_user.id,
            "<b>PERMINTAAN JOIN CHANNEL YMOVIEZ REBORN</b>\n\nSebelum masuk ke channel ada tes kejujuran, apakah anda sudah membaca catatan di @YMovieZ_New? Jika sudah silahkan klik <b>Sudah</b>, jika kamu berbohong resiko kamu tanggung sendiri 😶‍🌫️.\n\nBot by @YasirPediaChannel",
            disable_web_page_preview=True,
            reply_markup=markup,
        )
    #except Exception as err:
        #logging.info(err)

@app.on_callback_query(filters.regex(r"^approve"))
async def approve_chat(c, q):
    i, chat = q.data.split("_")
    await q.message.edit("Yeayy, selamat kamu bisa bergabung di Channel YMovieZ Reborn...")
    await c.approve_chat_join_request(chat, q.from_user.id)


@app.on_callback_query(filters.regex(r"^declined"))
async def decline_chat(c, q):
    i, chat = q.data.split("_")
    await q.message.edit("Yahh, kamu ditolak join channel. Biasakan rajin membaca yahhh..")
    await c.decline_chat_join_request(chat, q.from_user.id)


# Todo: Add exception if bot blocked
