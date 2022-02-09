from pyrogram.types import ChatPermissions
from pyrogram import Client, __version__, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import pytz
import urllib
import requests
from bot import app
from datetime import datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

async def job_close():
    now = datetime.now(pytz.timezone('Asia/Jakarta'))
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    month = ['Unknown', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    tgl = now.strftime('%d')
    tahun = now.strftime('%Y')
    jam = now.strftime('%H:%M')
    await app.send_sticker(-1001128045651, "CAACAgQAAxkDAAEDfNhgygZBqbTlbOQ6Gk3CmtD-bnkRDAACLxsAAvEGNAY-qWSFYAqy3R4E")
    await app.set_chat_permissions(-1001128045651, ChatPermissions(can_send_messages=False, can_invite_users=True)
    )
    await app.send_message(
      -1001128045651, f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ Jam : {jam}\n\n**🌗 Mode Malam Aktif**\n`Grup ditutup dan semua member tidak akan bisa mengirim pesan. Selamat beristirahat dan bermimpi indah !!`\n\n~ Dbuat dengan Pyrogram v{__version__}..", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❤️", callback_data="nightmd")]])
    )

async def job_close_ymoviez():
    now = datetime.now(pytz.timezone('Asia/Jakarta'))
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    month = ['Unknown', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    tgl = now.strftime('%d')
    tahun = now.strftime('%Y')
    jam = now.strftime('%H:%M')
    await app.set_chat_permissions(-1001255283935, ChatPermissions(can_send_messages=False, can_invite_users=True)
    )
    await app.send_message(
      -1001255283935, f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ Jam : {jam}\n\n**🌗 Mode Malam Aktif**\n`Grup ditutup hingga jam 9 pagi. Selamat beristirahat.....`\n\n~ Dbuat dengan Pyrogram v{__version__}..", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❤️", callback_data="nightmd")]])
    )

async def job_open():
    now = datetime.now(pytz.timezone('Asia/Jakarta'))
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    month = ['Unknown', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    tgl = now.strftime('%d')
    tahun = now.strftime('%Y')
    jam = now.strftime('%H:%M')
    res = requests.get("http://python-api-zhirrr.herokuapp.com/api/randomquotes").json()
    quotes = urllib.parse.quote(res['quotes'])
    by = "@MissKatyRoBot"
    url = f"https://api.lolhuman.xyz/api/quotemaker2?apikey=d6933a59588ca5e57e7eb141&text={quotes}&author={by}"
    response = requests.get(url)
    if response.status_code == 200:
        with open("quotes.jpg", 'wb') as f:
         f.write(response.content)
    else:
        reqtemp = requests.get("https://bukrate.com/set_images/images?id=1754607&author=1512321&type=6")
        with open("quotes.jpg", 'wb') as f:
         f.write(reqtemp.content)
    await app.set_chat_permissions(-1001128045651, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_invite_users=True, can_add_web_page_previews=True, can_send_other_messages=False)
    )
    await app.send_photo(
        -1001128045651, "quotes.jpg", caption=f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ {jam}`\n\n🌗 Mode Malam Selesai\nSelamat pagi, grup kini telah dibuka semoga hari-harimu menyenangkan.`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❤️", callback_data="nightmd")]])
    )

async def job_open_ymoviez():
    now = datetime.now(pytz.timezone('Asia/Jakarta'))
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    month = ['Unknown', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    tgl = now.strftime('%d')
    tahun = now.strftime('%Y')
    jam = now.strftime('%H:%M')
    res = requests.get("http://python-api-zhirrr.herokuapp.com/api/randomquotes").json()
    quotes = urllib.parse.quote(res['quotes'])
    by = "@MissKatyRoBot"
    url = f"https://api.lolhuman.xyz/api/quotemaker2?apikey=d6933a59588ca5e57e7eb141&text={quotes}&author={by}"
    response = requests.get(url)
    if response.status_code == 200:
        with open("quotes.jpg", 'wb') as f:
         f.write(response.content)
    else:
        reqtemp = requests.get("https://bukrate.com/set_images/images?id=1754607&author=1512321&type=6")
        with open("quotes.jpg", 'wb') as f:
         f.write(reqtemp.content)
    await app.set_chat_permissions(-1001255283935, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_invite_users=True, can_add_web_page_previews=True, can_send_other_messages=True)
    )
    await app.send_photo(
        -1001255283935, "quotes.jpg", caption=f"📆 {days[now.weekday()]}, {tgl} {month[now.month]} {tahun}\n⏰ {jam}`\n\n🌗 Mode Malam Selesai\nSelamat pagi, grup kini telah dibuka semoga hari-harimu menyenangkan.`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❤️", callback_data="nightmd")]])
    )

@app.on_callback_query(filters.regex(r"^nightmd$"))
async def _callbackanightmd(c: Client, q: CallbackQuery):
      await q.answer(f"🔖 Hai, Aku MissKatyRoBot dibuat menggunakan Pyrogram v{__version__}.\n\nMau buat bot seperti ini? Yuuk belajar di @botindonesia\nOwner: @YasirArisM", show_alert=True)

scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_close, trigger="cron", hour=22, minute=0)
scheduler.add_job(job_close_ymoviez, trigger="cron", hour=22, minute=15)
scheduler.add_job(job_open, trigger="cron", hour=6, minute=0)
scheduler.add_job(job_open_ymoviez, trigger="cron", hour=9, minute=0)
scheduler.start()
