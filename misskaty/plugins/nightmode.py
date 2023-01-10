# Auto Close and Open Group, I dont have time to add Database Support
import traceback
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, __version__, filters
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from misskaty import BOT_USERNAME, app
from misskaty.vars import LOG_CHANNEL, NIGHTMODE


# Check calculate how long it will take to Ramadhan
def puasa():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    tahun = now.strftime("%Y")
    bulan = now.strftime("%m")
    tgl = now.strftime("%d")
    jam = now.strftime("%H")
    menit = now.strftime("%M")
    detik = now.strftime("%S")
    x = datetime(int(tahun), int(bulan), int(tgl), int(jam), int(menit), int(detik))
    y = datetime(2022, 4, 2, 0, 0, 0)
    return y - x


async def job_close():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    month = [
        "Unknown",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    tgl = now.strftime("%d")
    tahun = now.strftime("%Y")
    jam = now.strftime("%H:%M")
    try:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="❤️", callback_data="nightmd")]]
        )
        await app.set_chat_permissions(
            -1001128045651,
            ChatPermissions(can_send_messages=False, can_invite_users=True),
        )
        await app.send_message(
            -1001128045651,
            f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ Jam : {jam}\n\n**🌗 Mode Malam Aktif**\n`Grup ditutup dan semua member tidak akan bisa mengirim pesan. Selamat beristirahat dan bermimpi indah !!`",
            reply_markup=reply_markup,
        )
    except Exception:
        exc = traceback.format_exc()
        await app.send_message(LOG_CHANNEL, f"ERROR:\n<code>{exc}</code>")


async def job_close_ymoviez():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    month = [
        "Unknown",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    tgl = now.strftime("%d")
    tahun = now.strftime("%Y")
    jam = now.strftime("%H:%M")
    try:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="❤️", callback_data="nightmd")]]
        )
        await app.set_chat_permissions(
            -1001255283935,
            ChatPermissions(can_send_messages=False, can_invite_users=True),
        )
        await app.send_message(
            -1001255283935,
            f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ Jam : {jam}\n\n**🌗 Mode Malam Aktif**\n`Grup ditutup hingga jam 9 pagi. Selamat beristirahat.....`",
        )
    except Exception:
        exc = traceback.format_exc()
        await app.send_message(LOG_CHANNEL, f"ERROR:\n<code>{exc}</code>")


async def job_open():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    month = [
        "Unknown",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    tgl = now.strftime("%d")
    tahun = now.strftime("%Y")
    jam = now.strftime("%H:%M")
    try:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="❤️", callback_data="nightmd")]]
        )
        await app.set_chat_permissions(
            -1001128045651,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_invite_users=True,
                can_add_web_page_previews=True,
                can_send_other_messages=False,
            ),
        )
        await app.send_message(
            -1001128045651,
            f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ {jam}`\n\n🌗 Mode Malam Selesai\nSelamat pagi, grup kini telah dibuka semoga hari-harimu menyenangkan.`",
            reply_markup=reply_markup,
        )
    except Exception:
        exc = traceback.format_exc()
        await app.send_message(LOG_CHANNEL, f"ERROR:\n<code>{exc}</code>")


async def job_open_ymoviez():
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    month = [
        "Unknown",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    tgl = now.strftime("%d")
    tahun = now.strftime("%Y")
    jam = now.strftime("%H:%M")
    try:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="❤️", callback_data="nightmd")]]
        )
        await app.set_chat_permissions(
            -1001255283935,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_invite_users=True,
                can_add_web_page_previews=True,
                can_send_other_messages=True,
            ),
        )
        await app.send_message(
            -1001255283935,
            f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ {jam}`\n\n🌗 Mode Malam Selesai\nSelamat pagi, grup kini telah dibuka semoga hari-harimu menyenangkan.`",
            reply_markup=reply_markup,
        )
    except Exception:
        exc = traceback.format_exc()
        await app.send_message(LOG_CHANNEL, f"ERROR:\n<code>{exc}</code>")


@app.on_callback_query(filters.regex(r"^nightmd$"))
async def _callbackanightmd(c: Client, q: CallbackQuery):
    await q.answer(
        f"🔖 Hai, Aku {BOT_USERNAME} dibuat menggunakan Framework Pyrogram v{__version__} dan Python 3.10.\n\nMau buat bot seperti ini? Yuuk belajar di @botindonesia\nOwner: @YasirArisM",
        show_alert=True,
        cache_time=2160,
    )


scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
if NIGHTMODE:
    scheduler.add_job(job_close, trigger="cron", hour=22, minute=0)
    # scheduler.add_job(job_close_ymoviez, trigger="cron", hour=22, minute=0)
    scheduler.add_job(job_open, trigger="cron", hour=6, minute=0)
    # scheduler.add_job(job_open_ymoviez, trigger="cron", hour=10, minute=0)
    scheduler.start()
