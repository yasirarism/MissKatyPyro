"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant, UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.core.decorator.errors import capture_err


# Filters Approve User by bot in channel @YMovieZNew
@capture_err
@app.on_chat_join_request(filters.chat(-1001686184174))
async def approve_join_chat(c, m):
    try:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Sudah", callback_data=f"approve_{m.chat.id}"
                    ),
                    InlineKeyboardButton(
                        text="Belum", callback_data=f"declined_{m.chat.id}"
                    ),
                ]
            ]
        )
        await c.send_message(
            m.from_user.id,
            "<b>PERMINTAAN JOIN CHANNEL YMOVIEZ REBORN</b>\n\nSebelum masuk ke channel ada tes kejujuran, apakah anda sudah membaca catatan di @YMovieZ_New? Jika sudah silahkan klik <b>Sudah</b>, jika kamu berbohong resiko kamu tanggung sendiri 😶‍🌫️.\n\nBot by @YasirPediaChannel",
            disable_web_page_preview=True,
            reply_markup=markup,
        )
    except UserIsBlocked:
        await m.decline()


@app.on_callback_query(filters.regex(r"^approve"))
async def approve_chat(c, q):
    _, chat = q.data.split("_")
    try:
        await q.message.edit(
            "Yeayy, selamat kamu bisa bergabung di Channel YMovieZ Reborn..."
        )
        await c.approve_chat_join_request(chat, q.from_user.id)
    except UserAlreadyParticipant:
        await q.message.edit(
            "Kamu sudah di acc join grup, jadi ga perlu menekan button."
        )
    except Exception as err:
        await q.message.edit(err)


@app.on_callback_query(filters.regex(r"^declined"))
async def decline_chat(c, q):
    _, chat = q.data.split("_")
    try:
        await q.message.edit(
            "Yahh, kamu ditolak join channel. Biasakan rajin membaca yahhh.."
        )
        await c.decline_chat_join_request(chat, q.from_user.id)
    except UserAlreadyParticipant:
        await q.message.edit(
            "Kamu sudah di acc join grup, jadi ga perlu menekan button."
        )
    except Exception as err:
        await q.message.edit(err)
