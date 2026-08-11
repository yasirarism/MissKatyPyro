# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import random
import re
import shutil

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import enums, filters
from pyrogram import types as pyro_types
from pyrogram.errors import PeerIdInvalid, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.permissions import admins_in_chat
from misskaty.helper.time_gap import check_time_gap
from misskaty.helper.chat_utils import temp

from .pypi_search import PYPI_DICT
from .web_scraper import SCRAP_DICT, data_kuso
from .ytdl_plugins import YT_DB

chat = [-1001128045651, -1001255283935, -1001455886928]
REQUEST_DB = {}


# This modules is only working for my movies group to help collect a list of film requests by members.


# @app.on_message(filters.regex(r"alamu'?ala[iy]ku+m", re.I) & filters.chat(chat))
async def salamregex(_, message):
    await message.reply_text(text=f"Wa'alaikumsalam {message.from_user.mention} 😇")


# -1001255283935 is YMovieZ Group, and -1001575525902 is channel id which contains a collection of ddard member requests from the group.
@app.on_message(
    filters.regex(r"#request|#req", re.I)
    & (filters.text | filters.photo)
    & filters.chat(-1001255283935)
    & ~filters.channel
)
@capture_err
async def request_user(client, message):
    if message.sender_chat:
        return await message.reply(
            f"{message.from_user.mention} mohon gunakan akun asli saat request."
        )
    is_in_gap, sleep_time = await check_time_gap(message.from_user.id)
    if is_in_gap:
        return await message.reply(
            f"Sabar dikit napa.. Tunggu {sleep_time} detik lagi 🙄"
        )
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="💬 Lihat Pesan", url=f"https://t.me/c/1255283935/{message.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Tolak",
                    callback_data=f"rejectreq_{message.id}_{message.chat.id}",
                ),
                InlineKeyboardButton(
                    text="✅ Done",
                    callback_data=f"donereq_{message.id}_{message.chat.id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚠️ Tidak Tersedia",
                    callback_data=f"unavailablereq_{message.id}_{message.chat.id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Sudah Ada",
                    callback_data=f"dahada_{message.id}_{message.chat.id}",
                )
            ],
        ]
    )
    try:
        user_id = message.from_user.id
        if user_id in REQUEST_DB:
            REQUEST_DB[user_id] += 1
        else:
            REQUEST_DB[user_id] = 1
        if REQUEST_DB[user_id] > 3:
            return await message.reply(
                f"Mohon maaf {message.from_user.mention}, maksimal request hanya 3x perhari. Kalo mau tambah 5k per request 😝😝."
            )
        if message.text:
            forward = await client.send_message(
                -1001575525902,
                f"Request by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> (#id{message.from_user.id})\n\n{message.text}",
                reply_markup=markup,
            )
            markup2 = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⏳ Cek Status Request",
                            url=f"https://t.me/c/1575525902/{forward.id}",
                        )
                    ]
                ]
            )
        if message.photo:
            forward = await client.send_photo(
                -1001575525902,
                message.photo.file_id,
                caption=f"Request by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>  (#id{message.from_user.id})\n\n{message.caption}",
                reply_markup=markup,
            )
            markup2 = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⏳ Cek Status Request",
                            url=f"https://t.me/c/1575525902/{forward.id}",
                        )
                    ]
                ]
            )
        await message.reply_text(
            text=f"Hai {message.from_user.mention}, request kamu sudah dikirim yaa. Harap bersabar mungkin admin juga punya kesibukan lain.\n\n<b>Sisa Request:</b> {3 - REQUEST_DB[user_id]}x",
            reply_markup=markup2,
        )
    except Exception:
        pass


# To reduce cache and disk
async def clear_reqdict():
    SCRAP_DICT.clear()
    data_kuso.clear()
    REQUEST_DB.clear()
    PYPI_DICT.clear()
    YT_DB.clear()
    admins_in_chat.clear()
    temp.MELCOW.clear()
    shutil.rmtree("downloads", ignore_errors=True)
    shutil.rmtree("GensSS", ignore_errors=True)


# @app.on_message(
#     filters.regex(r"makasi|thank|terimakasih|terima kasih|mksh", re.I)
#     & filters.chat(chat)
# )
async def thankregex(_, message):
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


# ── Admin action callbacks (done / already-available / reject / unavailable) ──
# Payload: <action>_<message_id>_<chat_id> — diproduksi oleh request_user di atas.

# REQUEST_ACTIONS: action → (text dikirim ke grup request, heading status, tombol status)
REQUEST_ACTIONS = {
    "donereq": (
        "#Done\nDone ✅, Selamat menonton. Jika request tidak bisa dilihat digrup silahkan join channel melalui link private yang ada di @YMovieZ_New ...",
        "COMPLETED",
        ("✅ Request Completed", "reqcompl"),
    ),
    "dahada": (
        "#SudahAda\nFilm/series yang direquest sudah ada sebelumnya. Biasakan mencari terlebih dahulu..",
        "#AlreadyAvailable",
        ("🔍 Request Sudah Ada", "reqavailable"),
    ),
    "rejectreq": (
        "Mohon maaf, request kamu ditolak karena tidak sesuai rules. Harap baca rules grup no.6 yaa 🙃.",
        "REJECTED",
        ("🚫 Request Rejected", "reqreject"),
    ),
    "unavailablereq": (
        "Mohon maaf, request kamu tidak tersedia. Silahkan baca beberapa alasannya di channel @YMovieZ_New",
        "UNAVAILABLE",
        ("⚠️ Request Unavailable", "requnav"),
    ),
}

# REQUEST_ACTION_ALERTS: alert yang muncul saat admin menekan tombol aksi.
REQUEST_ACTION_ALERTS = {
    "donereq": "Request berhasil diselesaikan ✅",
    "dahada": "Done ✔️",
    "rejectreq": "Request berhasil ditolak 🚫",
    "unavailablereq": "Request tidak tersedia, mungkin belum rilis atau memang tidak tersedia versi digital.",
}

# REQUEST_STATUS_INFO: alert saat tombol status (yang muncul setelah aksi) ditekan.
REQUEST_STATUS_INFO = {
    "reqcompl": (
        "Request ini sudah terselesaikan 🥳, silahkan cek di channel atau grup yaa..",
        1000,
    ),
    "reqreject": (
        "Request ini ditolak 💔, silahkan cek rules grup yaa.",
        1000,
    ),
    "requnav": (
        "Request ini tidak tersedia ☹️, mungkin filmnya belum rilis atau memang tidak tersedia versi digital.",
        1000,
    ),
    "reqavailable": ("Request ini sudah ada, silahkan cari 🔍 di channelnya yaa 😉..", None),
}


@app.on_callback_query(filters.regex(r"^(donereq|dahada|rejectreq|unavailablereq)_"))
async def callback_request_action(c, q):
    action = q.data.split("_", 1)[0]
    action_cfg = REQUEST_ACTIONS.get(action)
    if action_cfg is None:
        return await q.answer()
    text, heading, (btn_text, btn_data) = action_cfg
    try:
        user = await c.get_chat_member(-1001201566570, q.from_user.id)
        if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
        ]:
            _, msg_id, chat_id = q.data.split("_")
            await c.send_message(
                chat_id=chat_id,
                text=text,
                reply_parameters=pyro_types.ReplyParameters(message_id=int(msg_id)),
            )

            original = q.message.caption or q.message.text or ""
            await q.message.edit_text(
                f"<b>{heading}</b>\n\n<s>{original}</s>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=btn_text, callback_data=btn_data)]]
                ),
            )
            await q.answer(REQUEST_ACTION_ALERTS.get(action, "Done ✔️"))
        else:
            await q.answer("Apa motivasi kamu menekan tombol ini?", show_alert=True)
    except UserNotParticipant:
        return await q.answer(
            "Apa motivasi kamu menekan tombol ini?", show_alert=True, cache_time=10
        )
    except PeerIdInvalid:
        return await q.answer(
            "Silahkan kirim pesan digrup supaya bot bisa merespon.",
            show_alert=True,
            cache_time=10,
        )


@app.on_callback_query(filters.regex(r"^(reqcompl|reqreject|requnav|reqavailable)$"))
async def callback_request_status(_, q):
    info = REQUEST_STATUS_INFO.get(q.data)
    if info is None:
        return await q.answer()
    text, cache_time = info
    kwargs = {"show_alert": True}
    if cache_time is not None:
        kwargs["cache_time"] = cache_time
    await q.answer(text, **kwargs)


scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(clear_reqdict, trigger="cron", hour=2, minute=0)
scheduler.start()