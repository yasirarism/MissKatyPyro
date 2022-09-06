import re
import random
from bot import app
from pyrogram import filters, Client, enums
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from bot.core.decorator.errors import capture_err
from bot.helper.time_gap import check_time_gap

chat = [-1001128045651, -1001255283935, -1001455886928]
REQUEST_DB = {}


@app.on_message(
    filters.regex(r"alamu'?ala[iy]ku+m", re.I) & filters.chat(chat))
async def start(_, message):
    await message.reply_text(
        text=f"Wa'alaikumsalam {message.from_user.mention} 😇")


@app.on_message(
    filters.regex(r"#request|#req", re.I) & (filters.text | filters.photo)
    & filters.chat(-1001255283935))
@capture_err
async def request_user(client, message):
    is_in_gap, sleep_time = await check_time_gap(message.from_user.id)
    if is_in_gap:
        await message.reply("🙄")
        return
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="💬 Lihat Pesan",
                                 url=f"https://t.me/c/1255283935/{message.id}")
        ],
        [
            InlineKeyboardButton(
                text="🚫 Tolak",
                callback_data=f"rejectreq_{message.id}_{message.chat.id}"),
            InlineKeyboardButton(
                text="✅ Done",
                callback_data=f"donereq_{message.id}_{message.chat.id}")
        ],
        [
            InlineKeyboardButton(
                text="⚠️ Tidak Tersedia",
                callback_data=f"unavailablereq_{message.id}_{message.chat.id}")
        ],
        [
            InlineKeyboardButton(
                text="🔍 Sudah Ada",
                callback_data=f"dahada_{message.id}_{message.chat.id}")
        ],
    ])
    try:
        user_id = message.from_user.id
        if user_id in REQUEST_DB:
            REQUEST_DB[user_id] += 1
        else:
            REQUEST_DB[user_id] = 1
        if REQUEST_DB[user_id] > 3:
            return await message.reply(
                f"Mohon maaf {message.from_user.mention}, maksimal request hanya 3x perhari. Kalo mau tambah 10k per request 😝😝."
            )
        if message.text:
            forward = await client.send_message(
                -1001575525902,
                f"Request by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> (#id{message.from_user.id})\n\n{message.text}",
                reply_markup=markup)
            markup2 = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="⏳ Cek Status Request",
                    url=f"https://t.me/c/1575525902/{forward.id}")
            ]])
        if message.photo:
            forward = await client.send_photo(
                -1001575525902,
                message.photo.file_id,
                caption=
                f"Request by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n\n{message.caption}",
                reply_markup=markup)
            markup2 = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="⏳ Cek Status Request",
                    url=f"https://t.me/c/1575525902/{forward.id}")
            ]])
        await message.reply_text(
            text=
            f"Hai {message.from_user.mention}, request kamu sudah dikirim yaa. Harap bersabar mungkin admin juga punya kesibukan lain.\n\n<b>Sisa Request:</b> {3 - REQUEST_DB[user_id]}x",
            quote=True,
            reply_markup=markup2)
    except:
        pass


def clear_reqdict():
    REQUEST_DB.clear()


# @app.on_message(filters.regex(r"makasi|thank|terimakasih|terima kasih|mksh", re.I) & filters.chat(chat))
async def start(_, message):
    pesan = [
        f"Sama-sama {message.from_user.first_name}",
        f"You're Welcome {message.from_user.first_name}",
        "Oke..",
        "Yoi..",
        "Terimakasih Kembali..",
        "Sami-Sami...",
        "Sama-sama, senang bisa membantu..",
        f"Yups, Sama-sama {message.from_user.first_name}",
        "Okayyy...",
    ]
    await message.reply_text(text=random.choice(pesan))


@app.on_callback_query(filters.regex(r"^donereq"))
@capture_err
async def _callbackreq(c: Client, q: CallbackQuery):
    try:
        user = await c.get_chat_member(-1001686184174, q.from_user.id)
    except:
        pass
    if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER
    ]:
        i, msg_id, chat_id = q.data.split("_")
        await c.send_message(
            chat_id=chat_id,
            text=
            "#Done\nDone ✅, Selamat menonton. Jika request tidak bisa dilihat digrup silahkan join channel melalui link private yang ada di @YMovieZ_New ...",
            reply_to_message_id=int(msg_id),
        )

        if q.message.caption:
            await q.message.edit_text(
                f"<b>COMPLETED</b>\n\n<s>{q.message.caption}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="✅ Request Completed",
                                         callback_data="reqcompl")
                ]]))
        else:
            await q.message.edit_text(
                f"<b>COMPLETED</b>\n\n<s>{q.message.text}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="✅ Request Completed",
                                         callback_data="reqcompl")
                ]]))
        await q.answer("Request berhasil diselesaikan ✅")
    else:
        await q.answer("Apa motivasi kamu menekan tombol ini?",
                       show_alert=True)


@app.on_callback_query(filters.regex(r"^dahada"))
@capture_err
async def _callbackreqada(c: Client, q: CallbackQuery):
    try:
        user = await c.get_chat_member(-1001686184174, q.from_user.id)
    except:
        pass
    if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER
    ]:
        i, msg_id, chat_id = q.data.split("_")
        await c.send_message(
            chat_id=chat_id,
            text=
            "#Film/series yang direquest sudah ada sebelumnya. Biasakan mencari terlebih dahulu..",
            reply_to_message_id=int(msg_id),
        )

        if q.message.caption:
            await q.message.edit_text(
                f"<b>#AlreadyAvailable</b>\n\n<s>{q.message.caption}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="🔍 Request Sudah Ada",
                                         callback_data="reqavailable")
                ]]))
        else:
            await q.message.edit_text(
                f"<b>Already Available</b>\n\n<s>{q.message.text}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="🔍 Request Sudah Ada",
                                         callback_data="reqavailable")
                ]]))
        await q.answer("Done")
    else:
        await q.answer("Apa motivasi kamu menekan tombol ini?",
                       show_alert=True)


@app.on_callback_query(filters.regex(r"^rejectreq"))
@capture_err
async def _callbackreject(c: Client, q: CallbackQuery):
    try:
        user = await c.get_chat_member(-1001686184174, q.from_user.id)
    except:
        pass
    if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER
    ]:
        i, msg_id, chat_id = q.data.split("_")
        await c.send_message(
            chat_id=chat_id,
            text=
            "Mohon maaf, request kamu ditolak karena tidak sesuai rules. Harap baca rules nya no.6 yaa 🙃.",
            reply_to_message_id=int(msg_id),
        )

        if q.message.caption:
            await q.message.edit_text(
                f"<b>REJECTED</b>\n\n<s>{q.message.caption}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="🚫 Request Rejected",
                                         callback_data="reqreject")
                ]]))
        else:
            await q.message.edit_text(
                f"<b>REJECTED</b>\n\n<s>{q.message.text}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="🚫 Request Rejected",
                                         callback_data="reqreject")
                ]]))
        await q.answer("Requests berhasil ditolak 🚫")
    else:
        await q.answer("Apa motivasi kamu menekan tombol ini?",
                       show_alert=True)


@app.on_callback_query(filters.regex(r"^unavailablereq"))
@capture_err
async def _callbackunav(c: Client, q: CallbackQuery):
    try:
        user = await c.get_chat_member(-1001686184174, q.from_user.id)
    except:
        pass
    if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER
    ]:
        i, msg_id, chat_id = q.data.split("_")
        await c.send_message(
            chat_id=chat_id,
            text=
            "Mohon maaf, request kamu tidak tersedia, mungkin belum rilis atau memang ga ada versi digital..",
            reply_to_message_id=int(msg_id),
        )

        if q.message.caption:
            await q.message.edit_text(
                f"<b>UNAVAILABLE</b>\n\n<s>{q.message.caption}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="⚠️ Request Unavailable",
                                         callback_data="requnav")
                ]]))
        else:
            await q.message.edit_text(
                f"<b>UNAVAILABLE</b>\n\n<s>{q.message.text}</s>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="⚠️ Request Unavailable",
                                         callback_data="requnav")
                ]]))
        await q.answer(
            "Request tidak tersedia, mungkin belum rilis atau memang tidak tersedia versi digital."
        )
    else:
        await q.answer("Apa motivasi kamu menekan tombol ini?",
                       show_alert=True)


@app.on_callback_query(filters.regex(r"^reqcompl$"))
@capture_err
async def _callbackaft_done(c: Client, q: CallbackQuery):
    await q.answer(
        "Request ini sudah terselesaikan 🥳, silahkan cek di channel atau grup yaa..",
        show_alert=True)


@app.on_callback_query(filters.regex(r"^reqreject$"))
@capture_err
async def _callbackaft_rej(c: Client, q: CallbackQuery):
    await q.answer(
        "Request ini ditolak 💔, silahkan cek rules grup yaa. Jika belum paham bisa tanya ke admin lain digrup.",
        show_alert=True)


@app.on_callback_query(filters.regex(r"^requnav$"))
@capture_err
async def _callbackaft_unav(c: Client, q: CallbackQuery):
    await q.answer(
        "Request ini tidak tersedia 🥳, mungkin filmnya belum rilis atau memang tidak tersedia versi digital.",
        show_alert=True)


@app.on_callback_query(filters.regex(r"^reqavailable$"))
@capture_err
async def _callbackaft_dahada(c: Client, q: CallbackQuery):
    await q.answer(
        "Request ini sudah ada sebelumnya, silahkan cari 🔍 di channel atau grup yaa..",
        show_alert=True)


scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(clear_reqdict, trigger="cron", hour=7, minute=0)
scheduler.start()
