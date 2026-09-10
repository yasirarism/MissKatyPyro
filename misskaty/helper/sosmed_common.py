import asyncio
import os
from logging import getLogger
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from misskaty.helper.pyro_progress import progress_for_pyrogram


ACTIVE_TG_DOWNLOADS = {}


def _tg_download_cancel_markup(message_id, user_id):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data=f"tgdl_cancel#{message_id}#{user_id}")]]
    )


async def _tg_download_progress(current, total, label, message, start, dc_id, job_id, user_id):
    job = ACTIVE_TG_DOWNLOADS.get(int(job_id), {})
    if job.get("cancelled"):
        raise asyncio.CancelledError
    await progress_for_pyrogram(
        current, total, label, message, start, dc_id,
        reply_markup=_tg_download_cancel_markup(job_id, user_id),
    )


COOKIES_DEFAULT = os.path.join(os.getcwd(), "cookies.txt")


MAX_MEDIA = 50


MAX_CAPTION = 2500


def _resolve_cookies_path() -> str | None:
    for env in ("SOCMED_COOKIES_FILE", "IG_COOKIES_FILE"):
        path = os.environ.get(env)
        if path and os.path.exists(path):
            return path
    if os.path.exists(COOKIES_DEFAULT):
        return COOKIES_DEFAULT
    return None


def _load_netscape_cookies(path: str, domains=("instagram.com",)) -> dict:
    cookies: dict = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("# "):
                    continue
                if line.startswith("#HttpOnly_"):
                    line = line[len("#HttpOnly_") :]
                parts = line.split("\t")
                if len(parts) < 7:
                    continue
                domain, _flag, _path, _secure, _expiry, name, value = parts[:7]
                if any(d in domain for d in domains):
                    cookies[name] = value
    except Exception as e:
        LOGGER.warning("igdl gagal baca cookies.txt (%s): %s", path, e.__class__.__name__)
    return cookies


def _session_with_cookies(domains=("instagram.com",), use_cookies: bool = True):
    s = cffi_requests.Session(impersonate="chrome")
    if not use_cookies:
        return s
    path = _resolve_cookies_path()
    if path:
        cookies = _load_netscape_cookies(path, domains)
        if cookies:
            s.cookies.update(cookies)
            LOGGER.info("sosmed cookies.txt dipakai (%d cookie)", len(cookies))
    return s


def _ydl_cookie_opts() -> dict:
    path = os.environ.get("YTDL_COOKIE_FILE") or _resolve_cookies_path()
    return {"cookiefile": path} if path and os.path.exists(path) else {}


def _parse_duration(seconds) -> str:
    try:
        total = int(round(float(seconds)))
    except Exception:
        return "-"
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _fmt_num(n) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


LOGGER = getLogger("MissKaty")


try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None


try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None
