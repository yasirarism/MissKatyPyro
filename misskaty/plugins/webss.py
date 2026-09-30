# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2026-09-30 10:30:00
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import os
import socket
from logging import getLogger
from urllib.parse import urlparse

from pyrogram import filters
from pyrogram.types import Message

from misskaty import app
from misskaty.core.decorator import new_task
from misskaty.helper.http import fetch
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger("MissKaty")

__MODULE__ = "WebSS"
__HELP__ = """
/webss [url] - Screenshot halaman web (desktop 1280x900, viewport saja).
/webss [url] -m - Ukuran mobile 390x844.
/webss [url] -f - Full page (auto-scroll sampai bawah).
/webss [url] -p - Kirim sebagai PDF.
/webss [url] -w 1440 -h 900 - Ukuran custom (lebar 100-3840, tinggi 100-5000).
/webss [url] -d 3000 - Tambahan jeda tunggu (ms, maks 15000).
/webss [url] -q - Kirim sebagai dokumen (tanpa kompresi Telegram).
"""

# Endpoint milik sendiri (project WebSnap). Bisa dioverride lewat env WEBSS_API_BASE.
DEFAULT_API_BASE = "https://webss.yasirweb.eu.org"

# Preset desktop disamakan dengan webss.yasirweb.eu.org — viewport saja, bukan full page.
DESKTOP_SIZE = (1280, 900)
MOBILE_SIZE = (390, 844)

MIN_DIM, MAX_WIDTH, MAX_HEIGHT = 100, 3840, 5000
MAX_DELAY = 15000
DOWNLOAD_TIMEOUT = 90
MAX_CAPTION = 900

FORMAT_ALIAS = {"-p": "pdf", "--pdf": "pdf", "pdf": "pdf", "-png": "png", "--png": "png", "png": "png"}


def _api_base() -> str:
    return (os.environ.get("WEBSS_API_BASE") or DEFAULT_API_BASE).rstrip("/")


def _parse_args(args: list[str]) -> tuple[dict, str]:
    """Parse argumen command. Mengembalikan (opts, error_code)."""
    opts = {
        "url": None,
        "full": False,
        "mobile": False,
        "format": "jpg",
        "width": None,
        "height": None,
        "delay": None,
        "doc": False,
    }

    if not args:
        return opts, "no_url"

    i = 0
    while i < len(args):
        arg = args[i]
        low = arg.lower()

        if low in ("-f", "--full", "full"):
            opts["full"] = True
        elif low in ("-m", "--mobile", "mobile"):
            opts["mobile"] = True
        elif low in ("-q", "--doc", "--document"):
            opts["doc"] = True
        elif low in FORMAT_ALIAS:
            opts["format"] = FORMAT_ALIAS[low]
        elif low in ("-w", "--width", "-h", "--height", "-d", "--delay"):
            value = args[i + 1] if i + 1 < len(args) else None

            if value is None or not value.isdigit():
                return opts, f"butuh_angka:{arg}"

            number = int(value)

            if low in ("-w", "--width"):
                if not MIN_DIM <= number <= MAX_WIDTH:
                    return opts, f"lebar:{MIN_DIM}-{MAX_WIDTH}"
                opts["width"] = number
            elif low in ("-h", "--height"):
                if not MIN_DIM <= number <= MAX_HEIGHT:
                    return opts, f"tinggi:{MIN_DIM}-{MAX_HEIGHT}"
                opts["height"] = number
            else:
                opts["delay"] = max(0, min(number, MAX_DELAY))

            i += 1
        elif not arg.startswith("-") and opts["url"] is None:
            opts["url"] = arg

        i += 1

    if not opts["url"]:
        return opts, "no_url"

    # Ukuran custom cukup satu sisi; sisi lain mengikuti preset desktop.
    if opts["width"] and not opts["height"]:
        opts["height"] = DESKTOP_SIZE[1]
    elif opts["height"] and not opts["width"]:
        opts["width"] = DESKTOP_SIZE[0]

    return opts, ""


def _build_params(opts: dict, full_page: bool) -> dict:
    """Parameter query untuk GET /api/screenshot."""
    if opts["width"] and opts["height"]:
        res_x, res_y = opts["width"], opts["height"]
    elif opts["mobile"]:
        res_x, res_y = MOBILE_SIZE
    else:
        res_x, res_y = DESKTOP_SIZE

    return {
        "url": opts["url"],
        "resX": res_x,
        "resY": res_y,
        # scale=1 wajib: tanpa ini preset mobile memakai @3x (390x844 → 1170x2532).
        "scale": 1,
        "format": opts["format"],
        "fullPage": "true" if full_page else "false",
        "waitTime": opts["delay"] if opts["delay"] is not None else 1500,
    }


def _target_url(raw: str) -> str:
    raw = raw.strip()
    return raw if raw.lower().startswith(("http://", "https://")) else f"https://{raw}"


async def _host_ok(url: str) -> bool:
    """Cek DNS singkat: host mati langsung ditolak, tidak menunggu capture timeout."""
    try:
        host = urlparse(url).hostname
    except Exception:
        return False

    if not host or "." not in host:
        return False

    try:
        await asyncio.wait_for(asyncio.to_thread(socket.getaddrinfo, host, None), timeout=4)
    except Exception as e:
        LOGGER.info("webss dns gagal untuk %s (%s)", host, type(e).__name__)
        return False

    return True


async def _fetch_shot(params: dict) -> tuple[bytes, dict]:
    """Ambil hasil capture. `info['error']` terisi bila gagal."""
    try:
        res = await fetch.get(
            f"{_api_base()}/api/screenshot",
            params=params,
            timeout=DOWNLOAD_TIMEOUT,
            follow_redirects=True,
        )
    except Exception as e:
        LOGGER.warning("webss request gagal (%s): %s", e.__class__.__name__, str(e)[:120])
        return b"", {"error": "timeout" if "timeout" in str(e).lower() else "request_failed"}

    if res.status_code != 200:
        detail = ""
        try:
            detail = (res.json() or {}).get("error", "")
        except Exception:
            detail = (res.text or "")[:120]

        LOGGER.warning("webss http %s: %s", res.status_code, detail)
        return b"", {"error": "http", "status": res.status_code, "detail": detail}

    data = res.content

    if not data:
        return b"", {"error": "empty"}

    return data, {
        "error": None,
        "bytes": len(data),
        "content_type": (res.headers.get("content-type") or "").split(";")[0].strip(),
        "viewport": res.headers.get("x-snapshot-viewport") or "",
        "clipped": res.headers.get("x-snapshot-clipped") == "1",
        "blocked": res.headers.get("x-snapshot-blocked") or "0",
        "elapsed_ms": res.headers.get("x-snapshot-elapsed") or "",
    }


async def _capture(opts: dict) -> tuple[bytes, dict]:
    """Capture sekali. Kalau full page ditolak server (batas tinggi jalur sinkron), ulangi viewport saja."""
    data, info = await _fetch_shot(_build_params(opts, full_page=opts["full"]))

    if info.get("error") == "http" and opts["full"]:
        data2, info2 = await _fetch_shot(_build_params(opts, full_page=False))

        if not info2.get("error"):
            info2["fallback"] = True
            return data2, info2

    return data, info


def _file_path(user_id: int, fmt: str) -> str:
    os.makedirs("downloads", exist_ok=True)
    return os.path.join("downloads", f"webSS_{user_id}.{fmt}")


def _credit(opts: dict, info: dict, strings) -> str:
    """Caption singkat: sumber, ukuran viewport, dan mode."""
    if info.get("viewport"):
        size = info["viewport"]
    elif opts["width"] and opts["height"]:
        size = f"{opts['width']}x{opts['height']}"
    else:
        size = f"{DESKTOP_SIZE[0]}x{DESKTOP_SIZE[1]}"

    mode = "full page" if opts["full"] and not info.get("fallback") else "viewport"
    parts = [strings("str_credit"), f"{size} · {mode}"]

    if info.get("fallback"):
        parts.append(strings("ss_fallback_note"))

    if info.get("clipped"):
        parts.append(strings("ss_clipped_note"))

    return " · ".join(parts)[:MAX_CAPTION]


def _error_text(error: str, strings) -> str:
    if error == "timeout":
        return strings("ss_timeout_str")
    if error == "request_failed":
        return strings("ss_unreachable_str")
    if error == "dns":
        return strings("ss_dns_str")
    if error.startswith("butuh_angka:"):
        return strings("ss_need_number").format(flag=error.split(":", 1)[1])
    if error.startswith("lebar:"):
        return strings("ss_bad_width").format(range=error.split(":", 1)[1])
    if error.startswith("tinggi:"):
        return strings("ss_bad_height").format(range=error.split(":", 1)[1])
    return strings("ss_failed_str").format(err=error)


@app.on_message(filters.command(["webss"], COMMAND_HANDLER))
@new_task
@use_chat_lang()
async def take_ss(_, ctx: Message, strings):
    opts, error = _parse_args(list(ctx.command[1:]))

    if error == "no_url":
        return await ctx.reply(__HELP__.strip(), del_in=30)

    if error:
        return await ctx.reply(_error_text(error, strings), del_in=12)

    opts["url"] = _target_url(opts["url"])

    if not await _host_ok(opts["url"]):
        return await ctx.reply(_error_text("dns", strings), del_in=12)

    user_id = ctx.from_user.id if ctx.from_user else ctx.chat.id
    msg = await ctx.reply(strings("wait_str"))

    data, info = await _capture(opts)

    if info.get("error"):
        if info.get("error") == "http":
            detail = info.get("detail") or f"HTTP {info.get('status')}"
            return await msg.edit(strings("ss_failed_str").format(err=detail))

        return await msg.edit(_error_text(info["error"], strings))

    path = _file_path(user_id, opts["format"])

    try:
        with open(path, "wb") as fh:
            fh.write(data)

        caption = _credit(opts, info, strings)

        # PNG/PDF/dokumen dikirim tanpa kompresi Telegram; JPG cukup sebagai foto.
        if opts["doc"] or opts["format"] in ("png", "pdf"):
            await ctx.reply_document(path, caption=caption)
        else:
            await ctx.reply_photo(path, caption=caption)

        await msg.delete_msg()
    finally:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
