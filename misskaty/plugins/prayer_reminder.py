# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
"""Chat-configurable prayer time reminder using api.myquran.com."""

import datetime
from contextlib import suppress
from html import escape
from logging import getLogger
from typing import Optional

import aiohttp
import pytz
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
    Message,
)

from database.prayer_reminder_db import (
    get_enabled_prayer_configs,
    get_prayer_config,
    set_prayer_city,
    set_prayer_enabled,
    set_prayer_last_sent,
    set_prayer_schedule,
    set_prayer_target,
)
from misskaty import app, scheduler
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger("MissKaty")

__MODULE__ = "PrayerReminder"
__HELP__ = """<b>Reminder sholat otomatis dari api.myquran.com</b>

<b>Commands:</b>
/prayerreminder - buka panel pengaturan dengan tombol
/prayerreminder sura - cari kota, lalu pilih lewat tombol
/prayerreminder test - kirim contoh reminder ke target tersimpan

Setting disimpan per chat di database. Gunakan tombol panel untuk ON/OFF dan set target chat/topic.
"""

CITY_LIST_URL = "https://api.myquran.com/v3/sholat/kabkota/semua"
SCHEDULE_URL = "https://api.myquran.com/v3/sholat/jadwal/{city_id}/{date}?tz={timezone}"
WEEKDAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
MONTHS_ID = [
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
PRAYER_KEYS = ["subuh", "dzuhur", "ashar", "maghrib", "isya"]
EMOJI_MAP = {
    "subuh": "🌅",
    "dzuhur": "🌞",
    "ashar": "🔘",
    "maghrib": "🌤",
    "isya": "⭐",
}
LABEL_TEXT = {
    "subuh": "Subuh",
    "dzuhur": "Dzuhur",
    "ashar": "Ashar",
    "maghrib": "Maghrib",
    "isya": "Isya",
}
PRAYER_ALIASES = {
    "subuh": ("subuh", "shubuh", "fajr"),
    "dzuhur": ("dzuhur", "zuhur", "dhuhur", "dhuhr"),
    "ashar": ("ashar", "asar", "asr"),
    "maghrib": ("maghrib", "magrib"),
    "isya": ("isya", "isya\'", "isha"),
}


def _prayer_label(prayer: str, now: datetime.datetime) -> str:
    if prayer == "dzuhur" and now.weekday() == 4:
        return "Jum'at"
    return prayer.capitalize()


def _format_reminder(
    prayer: str, jadwal: dict, now: datetime.datetime, city_name: str
) -> str:
    weekday = WEEKDAYS_ID[now.weekday()]
    month = MONTHS_ID[now.month - 1]
    rows = []
    for key in PRAYER_KEYS:
        label = LABEL_TEXT[key]
        time_value = jadwal.get(key, "-")
        current = "<tg-emoji emoji-id='6039454987250044861'>✅</tg-emoji>" if key == prayer else ""
        rows.append(
            "<tr>"
            f"<td>{escape(EMOJI_MAP[key])} <b>{escape(label)}</b></td>"
            f"<td align=\"center\"><code>{escape(time_value)}</code> {escape(current)}</td>"
            "</tr>"
        )

    table = (
        "<table bordered striped>"
        "<caption>Jadwal Hari Ini</caption>"
        "<tr><th>Sholat</th><th>Waktu</th></tr>"
        f"{''.join(rows)}"
        "</table>"
    )
    return (
        f"🕌 <b>Waktunya Sholat {escape(_prayer_label(prayer, now))}</b><br>"
        f"<b>Wilayah:</b> {escape(city_name)}<br>"
        f"<b>Tanggal:</b> {weekday}, {now.strftime('%d')} {month} {now.year}<br>"
        f"{table}"
        "<aside>Sumber:<cite>Kemenag RI</cite></aside>"
    )


def _current_prayer(jadwal: dict, now: datetime.datetime) -> Optional[str]:
    for key in PRAYER_KEYS:
        try:
            hour, minute = map(int, jadwal[key].split(":")[:2])
        except (KeyError, TypeError, ValueError):
            continue
        start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if start <= now < start + datetime.timedelta(minutes=1):
            return key
    return None


def _find_jadwal_payload(payload) -> dict:
    if isinstance(payload, dict):
        lowered_keys = {str(key).lower() for key in payload}
        if any(alias in lowered_keys for aliases in PRAYER_ALIASES.values() for alias in aliases):
            return payload
        for value in payload.values():
            found = _find_jadwal_payload(value)
            if found:
                return found
    if isinstance(payload, list):
        for item in payload:
            found = _find_jadwal_payload(item)
            if found:
                return found
    return {}


def _normalize_jadwal(payload) -> dict:
    jadwal = _find_jadwal_payload(payload)
    if not isinstance(jadwal, dict):
        return {}
    lowered = {str(key).lower(): value for key, value in jadwal.items()}
    normalized = {}
    for prayer, aliases in PRAYER_ALIASES.items():
        for alias in aliases:
            if alias in lowered and lowered[alias]:
                normalized[prayer] = str(lowered[alias])
                break
    return normalized


async def _fetch_json(url: str) -> Optional[dict]:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    LOGGER.warning("Prayer reminder API returned HTTP %s for %s", resp.status, url)
                    return None
                return await resp.json(content_type=None)
    except Exception as exc:
        LOGGER.warning("Failed to fetch prayer reminder API: %s", exc)
        return None


async def _fetch_jadwal(config: dict, now: datetime.datetime) -> Optional[dict]:
    date_str = now.strftime("%Y-%m-%d")
    data = await _fetch_json(
        SCHEDULE_URL.format(
            city_id=config["city_id"], date=date_str, timezone=config["timezone"]
        )
    )
    if not data:
        return None
    return _normalize_jadwal(data)


async def _get_cached_jadwal(config: dict, now: datetime.datetime) -> Optional[dict]:
    date_str = now.strftime("%Y-%m-%d")
    cached = config.get("schedule")
    if config.get("schedule_date") == date_str and isinstance(cached, dict):
        return cached

    jadwal = await _fetch_jadwal(config, now)
    if jadwal and all(key in jadwal for key in PRAYER_KEYS):
        await set_prayer_schedule(config["chat_id"], date_str, jadwal)
    return jadwal


async def _get_cities() -> list[dict]:
    data = await _fetch_json(CITY_LIST_URL)
    if not data or not data.get("status"):
        return []
    return data.get("data", [])


def _panel_markup(config: dict, user_id: int) -> InlineKeyboardMarkup:
    status_text = "🔴 Nonaktifkan" if config["enabled"] else "🟢 Aktifkan"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(status_text, callback_data=f"prtoggle#{user_id}")],
            [InlineKeyboardButton("📍 Set target chat/topic ini", callback_data=f"prtarget#{user_id}")],
            [InlineKeyboardButton("🧪 Test reminder", callback_data=f"prtest#{user_id}")],
            [InlineKeyboardButton("❌ Close", callback_data=f"prclose#{user_id}")],
        ]
    )


def _panel_text(config: dict) -> str:
    status = "Aktif" if config["enabled"] else "Nonaktif"
    return (
        "🕌 **Prayer Reminder**\n"
        f"Status: **{status}**\n"
        f"Kota: **{config['city_name']}** (`{config['city_id']}`)\n"
        f"Timezone: `{config['timezone']}`\n"
        f"Chat ID: `{config['chat_id'] or '-'}`\n"
        f"Thread ID: `{config['thread_id'] or '-'}`\n\n"
        "Cari kota dengan command: `/prayerreminder <kota>`"
    )


def _city_markup(cities: list[dict], user_id: int) -> InlineKeyboardMarkup:
    rows = []
    for city in cities[:10]:
        rows.append(
            [
                InlineKeyboardButton(
                    city["lokasi"][:35], callback_data=f"prcity#{user_id}#{city['id']}"
                )
            ]
        )
    rows.append([InlineKeyboardButton("↩️ Panel", callback_data=f"prpanel#{user_id}")])
    return InlineKeyboardMarkup(rows)


async def send_prayer_reminder(
    config: dict, force: bool = False, prayer: Optional[str] = None
):
    if not config.get("chat_id"):
        return False
    timezone = pytz.timezone(config["timezone"])
    now = datetime.datetime.now(timezone)
    jadwal = await _get_cached_jadwal(config, now)
    if not jadwal or any(key not in jadwal for key in PRAYER_KEYS):
        LOGGER.warning(
            "Prayer schedule is incomplete for chat_id=%s city_id=%s",
            config.get("chat_id"),
            config.get("city_id"),
        )
        return False
    prayer = prayer or _current_prayer(jadwal, now) or ("subuh" if force else None)
    if not prayer:
        return False
    sent_key = f"{now.strftime('%Y-%m-%d')}:{prayer}"
    if not force and config.get("last_sent") == sent_key:
        return False
    kwargs = {"message_thread_id": config.get("thread_id")} if config.get("thread_id") else {}
    html = _format_reminder(prayer, jadwal, now, config["city_name"])
    if hasattr(app, "send_rich_message"):
        await app.send_rich_message(
            config["chat_id"],
            InputRichMessage(html=html),
            **kwargs,
        )
    else:
        await app.send_message(config["chat_id"], html, **kwargs)
    if not force:
        await set_prayer_last_sent(config["chat_id"], sent_key)
    return True


def _job_id(chat_id: int, name: str) -> str:
    return f"prayer_reminder_{chat_id}_{name}"


def _remove_chat_jobs(chat_id: int):
    for key in [*PRAYER_KEYS, "refresh"]:
        with suppress(Exception):
            scheduler.remove_job(_job_id(chat_id, key))


async def send_scheduled_prayer(chat_id: int, prayer: str):
    config = await get_prayer_config(chat_id)
    if config.get("enabled"):
        await send_prayer_reminder(config, prayer=prayer)


async def refresh_prayer_jobs(chat_id: int):
    config = await get_prayer_config(chat_id)
    await sync_prayer_jobs(config)


async def sync_prayer_jobs(config: dict):
    chat_id = config["chat_id"]
    _remove_chat_jobs(chat_id)
    if not config.get("enabled"):
        return

    timezone = pytz.timezone(config["timezone"])
    now = datetime.datetime.now(timezone)
    jadwal = await _get_cached_jadwal(config, now)
    if not jadwal or any(key not in jadwal for key in PRAYER_KEYS):
        LOGGER.warning(
            "Cannot schedule prayer reminder for chat_id=%s because schedule is incomplete",
            chat_id,
        )
        return

    for prayer in PRAYER_KEYS:
        hour, minute = map(int, jadwal[prayer].split(":")[:2])
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_time <= now:
            continue
        scheduler.add_job(
            send_scheduled_prayer,
            "date",
            [chat_id, prayer],
            id=_job_id(chat_id, prayer),
            run_date=run_time,
            replace_existing=True,
            misfire_grace_time=60,
        )

    scheduler.add_job(
        refresh_prayer_jobs,
        "cron",
        [chat_id],
        id=_job_id(chat_id, "refresh"),
        hour=0,
        minute=5,
        timezone=timezone,
        replace_existing=True,
        misfire_grace_time=300,
    )


async def bootstrap_prayer_reminders():
    for config in await get_enabled_prayer_configs():
        await sync_prayer_jobs(config)


@app.on_message(filters.command(["prayerreminder", "sholatreminder"], COMMAND_HANDLER))
async def prayer_reminder_handler(_, msg: Message):
    config = await get_prayer_config(msg.chat.id)
    if len(msg.command) > 1 and msg.command[1].lower() == "test":
        sent = await send_prayer_reminder(config, force=True)
        return await msg.reply("✅ Test reminder sholat sudah dikirim." if sent else "⚠️ Target belum diset atau jadwal gagal diambil.")

    if len(msg.command) > 1:
        keyword = " ".join(msg.command[1:]).lower()
        cities = [city for city in await _get_cities() if keyword in city.get("lokasi", "").lower()]
        if not cities:
            return await msg.reply("⚠️ Kota tidak ditemukan atau API sedang bermasalah.")
        return await msg.reply(
            f"🔎 Hasil pencarian kota untuk: `{keyword}`",
            reply_markup=_city_markup(cities, msg.from_user.id),
        )

    await msg.reply(_panel_text(config), reply_markup=_panel_markup(config, msg.from_user.id))


@app.on_callback_query(filters.regex(r"^pr(toggle|target|test|close|panel|city)#"))
async def prayer_reminder_callback(_, query: CallbackQuery):
    parts = query.data.split("#")
    action = parts[0]
    user_id = int(parts[1])
    if query.from_user.id != user_id:
        return await query.answer("⚠️ Tombol ini bukan untuk kamu.", show_alert=True)

    config = await get_prayer_config(query.message.chat.id)
    if action == "prclose":
        return await query.message.delete()

    if action == "prpanel":
        return await query.message.edit(_panel_text(config), reply_markup=_panel_markup(config, user_id))

    if action == "prtoggle":
        if not config.get("chat_id"):
            return await query.answer("Set target chat/topic dulu.", show_alert=True)
        config = await set_prayer_enabled(query.message.chat.id, not config["enabled"])
        await sync_prayer_jobs(config)
        await query.answer("Reminder diaktifkan." if config["enabled"] else "Reminder dimatikan.")
        return await query.message.edit(_panel_text(config), reply_markup=_panel_markup(config, user_id))

    if action == "prtarget":
        config = await set_prayer_target(query.message.chat.id, query.message.message_thread_id)
        await sync_prayer_jobs(config)
        await query.answer("Target chat/topic disimpan.")
        return await query.message.edit(_panel_text(config), reply_markup=_panel_markup(config, user_id))

    if action == "prtest":
        sent = await send_prayer_reminder(config, force=True)
        return await query.answer("Test terkirim." if sent else "Target belum diset atau jadwal gagal diambil.", show_alert=not sent)

    if action == "prcity":
        city_id = parts[2]
        city = next((item for item in await _get_cities() if item.get("id") == city_id), None)
        if not city:
            return await query.answer("Kota tidak ditemukan.", show_alert=True)
        config = await set_prayer_city(query.message.chat.id, city["id"], city["lokasi"])
        await sync_prayer_jobs(config)
        await query.answer(f"Kota diset ke {city['lokasi']}.")
        return await query.message.edit(_panel_text(config), reply_markup=_panel_markup(config, user_id))


scheduler.add_job(
    bootstrap_prayer_reminders,
    "date",
    id="prayer_reminder_bootstrap",
    run_date=datetime.datetime.now() + datetime.timedelta(seconds=5),
    replace_existing=True,
    misfire_grace_time=60,
)
