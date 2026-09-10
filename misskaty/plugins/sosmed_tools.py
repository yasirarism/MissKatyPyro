# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 / 2026-09-10
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import base64
import contextlib
import json
import math
import os
import re
import time
from datetime import datetime
from logging import getLogger
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram import types as pyro_types
from pyrogram.file_id import FileId
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
)
from pySmartDL import SmartDL

from misskaty import app
from misskaty.core.decorator import capture_err, new_task
from misskaty.helper.http import fetch
from misskaty.helper.pyro_progress import humanbytes, progress_for_pyrogram
from misskaty.vars import COMMAND_HANDLER, OWNER_ID

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None

LOGGER = getLogger("MissKaty")

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

__MODULE__ = "SosmedTools"
__HELP__ = """
/igdl [link] atau /instadl [link] - Instagram post/reel sebagai slideshow rich message (media, likes, komentar, caption, metadata video).
/tiktokdl [link] - Download TikTok video.
/fbdl [link] - Facebook post/reel/video sebagai slideshow rich message.
  Metrik (reaksi/komentar/share) butuh cookies.txt akun Facebook.
/twitterdl [link] - Download video dari Twitter/X.
/ytdown [YT-DLP URL] - Download video/audio via yt-dlp.
/download [url] atau reply file - Download ke server (OWNER only).
/anon [reply file] - Upload file ke anonfiles.
"""


@app.on_message(filters.command(["anon"], COMMAND_HANDLER))
async def upload(bot, message):
    if not message.reply_to_message:
        return await message.reply("Please reply to media file.")
    vid = [
        message.reply_to_message.video,
        message.reply_to_message.document,
        message.reply_to_message.audio,
        message.reply_to_message.photo,
    ]
    media = next((v for v in vid if v is not None), None)
    if not media:
        return await message.reply("Unsupported media type..")
    m = await message.reply("Download your file to my Server...")
    now = time.time()
    dc_id = FileId.decode(media.file_id).dc_id
    fileku = await message.reply_to_message.download(
        progress=progress_for_pyrogram,
        progress_args=("Trying to download, please wait..", m, now, dc_id),
    )
    try:
        files = {"file": open(fileku, "rb")}
        await m.edit("Uploading to Anonfile, Please Wait||")
        callapi = await fetch.post("https://api.anonfiles.com/upload", files=files)
        text = callapi.json()
        output = f'<u>File Uploaded to Anonfile</u>\n\n📂 File Name: {text["data"]["file"]["metadata"]["name"]}\n\n📦 File Size: {text["data"]["file"]["metadata"]["size"]["readable"]}\n\n📥 Download Link: {text["data"]["file"]["url"]["full"]}'

        btn = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 Download 📥", url=f"{text['data']['file']['url']['full']}"
                    )
                ]
            ]
        )
        await m.edit(output, reply_markup=btn)
    except Exception as e:
        await bot.send_message(message.chat.id, text=f"Something Went Wrong!\n\n{e}")
    os.remove(fileku)


@app.on_message(filters.command(["download"], COMMAND_HANDLER) & filters.user(OWNER_ID))
@capture_err
@new_task
async def download(client, message):
    pesan = await message.reply_text("<emoji id=5319190934510904031>⏳</emoji> Processing..")
    if message.reply_to_message is not None:
        start_t = datetime.now()
        c_time = time.time()
        vid = [
            message.reply_to_message.video,
            message.reply_to_message.document,
            message.reply_to_message.audio,
            message.reply_to_message.photo,
        ]
        media = next((v for v in vid if v is not None), None)
        if not media:
            return await pesan.edit("Unsupported media type..")
        dc_id = FileId.decode(media.file_id).dc_id
        job_id = f"{message.chat.id}:{pesan.id}"
        user_id = message.from_user.id if message.from_user else OWNER_ID
        await pesan.edit(reply_markup=_tg_download_cancel_markup(job_id, user_id))
        download_task = asyncio.create_task(
            client.download_media(
                message=message.reply_to_message,
                progress=_tg_download_progress,
                progress_args=("Trying to download, sabar yakk..", pesan, c_time, dc_id, job_id, user_id),
            )
        )
        ACTIVE_TG_DOWNLOADS[job_id] = {"task": download_task, "user_id": user_id}
        try:
            the_real_download_location = await download_task
        except asyncio.CancelledError:
            ACTIVE_TG_DOWNLOADS.pop(job_id, None)
            with contextlib.suppress(Exception):
                await pesan.edit("❌ Download cancelled.")
            return
        ACTIVE_TG_DOWNLOADS.pop(job_id, None)
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await pesan.edit(
            f"Downloaded to <code>{the_real_download_location}</code> in <u>{ms}</u> seconds."
        )
    elif len(message.command) > 1:
        start_t = datetime.now()
        the_url_parts = " ".join(message.command[1:])
        url = the_url_parts.strip()
        custom_file_name = os.path.basename(url)
        if "|" in the_url_parts:
            url, custom_file_name = the_url_parts.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()
        download_file_path = os.path.join("downloads/", custom_file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False, timeout=10)
        try:
            downloader.start(blocking=False)
        except Exception as err:
            return await message.edit(str(err))
        c_time = time.time()
        while not downloader.isFinished():
            total_length = downloader.filesize or None
            downloaded = downloader.get_dl_size(human=True)
            display_message = ""
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed(human=True)
            progress_str = "[{0}{1}]\nProgress: {2}%".format(
                "".join(["●" for _ in range(math.floor(percentage / 5))]),
                "".join(["○" for _ in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )

            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = "<emoji id=5319190934510904031>⏳</emoji> Processing..\n"
                current_message += f"URL: <code>{url}</code>\n"
                current_message += (
                    f"File Name: <code>{unquote(custom_file_name)}</code>\n"
                )
                current_message += f"Speed: {speed}\n"
                current_message += f"{progress_str}\n"
                current_message += f"{downloaded} of {humanbytes(total_length)}\n"
                current_message += f"ETA: {estimated_total_time}"
                if round(diff % 10.00) == 0 and current_message != display_message:
                    await pesan.edit(
                        link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True), text=current_message
                    )
                    display_message = current_message
                    await asyncio.sleep(10)
            except Exception as e:
                LOGGER.info(str(e))
        if os.path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await pesan.edit(
                f"Downloaded to <code>{download_file_path}</code> in {ms} seconds"
            )
    else:
        await pesan.edit(
            "Reply to a Telegram Media, to download it to my local server."
        )


@app.on_callback_query(filters.regex(r"^tgdl_cancel#"))
async def tg_download_cancel(_, query):
    try:
        _, job_id, user_id = (query.data or "").split("#", 2)
    except ValueError:
        return await query.answer("Invalid task", True)
    if query.from_user.id != int(user_id):
        return await query.answer("Not yours!", True)
    job = ACTIVE_TG_DOWNLOADS.get(job_id)
    if not job:
        return await query.answer("Task already finished", True)
    task = job.get("task")
    if task and not task.done():
        task.cancel()
    await query.answer("Cancelling download...")


COOKIES_DEFAULT = os.path.join(os.getcwd(), "cookies.txt")
MAX_MEDIA = 50
MAX_CAPTION = 2500

_SJS_RE = re.compile(r'<script\b[^>]+\bdata-sjs>(\{.+?\})</script>')
_DASH_DURATION_RE = re.compile(r'duration="PT([\d.]+)S"')
_DASH_CODEC_RE = re.compile(r'codecs="([^"]+)"')


def _extract_post_id(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    m = re.search(r"^(?:p|reel|tv|reels)/([A-Za-z0-9_-]+)", path)
    if m:
        return m.group(1)
    m = re.search(r"([A-Za-z0-9_-]{10,})$", path)
    if m:
        return m.group(1)
    return url.strip()


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


def _find_polaris(obj, out: list):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "xig_polaris_media" and isinstance(v, dict):
                out.append(v)
            else:
                _find_polaris(v, out)
    elif isinstance(obj, list):
        for x in obj:
            _find_polaris(x, out)


def _best_image(node: dict) -> str | None:
    if not node:
        return None
    cands = ((node.get("image_versions2") or {}).get("candidates")) or []
    return cands[0]["url"] if cands else None


def _best_video(node: dict) -> str | None:
    if not node:
        return None
    vv = node.get("video_versions") or []
    return vv[0]["url"] if vv else None


def _parse_duration(seconds) -> str:
    try:
        total = int(round(float(seconds)))
    except Exception:
        return "-"
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _video_meta(node: dict) -> dict | None:
    if not node or not node.get("video_versions"):
        return None
    meta: dict = {}
    dash = node.get("video_dash_manifest") or ""
    m = _DASH_DURATION_RE.search(dash)
    if m:
        meta["duration"] = _parse_duration(m.group(1))
    w, h = node.get("original_width"), node.get("original_height")
    if w and h:
        meta["resolution"] = f"{w}x{h}"
    if node.get("has_audio") is not None:
        meta["audio"] = "ada" if node.get("has_audio") else "tanpa audio"
    qualities = node.get("number_of_qualities")
    if qualities:
        meta["qualities"] = str(qualities)
    codecs = sorted({c.split(".")[0] for c in _DASH_CODEC_RE.findall(dash)})
    if codecs:
        meta["codec"] = ", ".join(codecs)
    return meta or None


def _extract_sync(shortcode: str) -> dict:
    if not cffi_requests:
        return {"ok": False, "reason": "no_curl_cffi"}

    s = _session_with_cookies()

    try:
        r = s.get(f"https://www.instagram.com/p/{shortcode}/", timeout=30, max_redirects=10)
    except Exception as e:
        LOGGER.warning("igdl request gagal (%s): %s", e.__class__.__name__, str(e)[:100])
        try:
            s = _session_with_cookies(use_cookies=False)
            r = s.get(f"https://www.instagram.com/p/{shortcode}/", timeout=30, max_redirects=10)
        except Exception as e2:
            LOGGER.warning("igdl retry tanpa cookie gagal: %s", str(e2)[:100])
            return {"ok": False, "reason": "request_failed"}
    if r.status_code == 429:
        return {"ok": False, "reason": "rate_limited"}
    if r.status_code != 200:
        return {"ok": False, "reason": f"http_{r.status_code}"}
    html = r.text

    if "xig_polaris_media" not in html:
        return {"ok": False, "reason": "unavailable_or_private"}

    medias: list = []
    for raw in _SJS_RE.findall(html):
        try:
            tree = json.loads(raw)
        except Exception:
            continue
        _find_polaris(tree, medias)
    if not medias:
        return {"ok": False, "reason": "unavailable_or_private"}

    media = medias[0]
    product = media.get("if_not_gated_logged_out") or media
    user = product.get("user") or {}

    media_items: list = []
    nodes = product.get("carousel_media") or [product]
    for node in nodes:
        vurl = _best_video(node)
        item = {
            "type": "video" if vurl else "photo",
            "url": vurl or _best_image(node),
        }
        if vurl:
            item["meta"] = _video_meta(node)
        media_items.append(item)

    media_items = [m for m in media_items if m["url"]]
    video_meta = next((m.get("meta") for m in media_items if m.get("meta")), None)
    n_video = sum(1 for m in media_items if m["type"] == "video")

    return {
        "ok": True,
        "owner": (user.get("username") or "").strip(),
        "full_name": (user.get("full_name") or "").strip(),
        "verified": bool(user.get("is_verified")),
        "likes": int(product.get("like_count") or 0),
        "comments": int(product.get("comment_count") or 0),
        "timestamp": product.get("taken_at"),
        "caption": (product.get("caption") or {}).get("text") or "",
        "media": media_items,
        "n_video": n_video,
        "video_meta": video_meta,
        "shortcode": shortcode,
    }


async def _get_instagram_data(link: str) -> dict:
    shortcode = _extract_post_id(link)
    if not shortcode:
        return {"ok": False, "reason": "invalid_url"}
    try:
        return await asyncio.to_thread(_extract_sync, shortcode)
    except Exception as e:
        LOGGER.warning("igdl extract gagal: %s", e)
        return {"ok": False, "reason": f"exception:{e.__class__.__name__}"}





def _fmt_num(n) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_slideshow(data: dict) -> str:
    media = (data.get("media") or [])[:MAX_MEDIA]
    if not media:
        return ""
    items = []
    for item in media:
        src = _esc(item["url"])
        if item["type"] == "video":
            items.append(f'<video src="{src}"/>')
        else:
            items.append(f'<img src="{src}"/>')
    owner = _esc(data.get("owner") or "Instagram")
    label = f"{len(media)} media" if len(media) > 1 else "1 media"
    return f"<tg-slideshow>{''.join(items)}<figcaption>@{owner} · {label}</figcaption></tg-slideshow>"


def _build_video_details(data: dict) -> str:
    meta = data.get("video_meta")
    if not meta:
        return ""
    n_video = data.get("n_video", 1)
    rows = []
    if meta.get("duration"):
        rows.append(f"<p>⏱ <b>Durasi:</b> {meta['duration']}</p>")
    if meta.get("resolution"):
        rows.append(f"<p>📐 <b>Resolusi:</b> {meta['resolution']}</p>")
    if meta.get("qualities"):
        rows.append(f"<p>🎚 <b>Kualitas:</b> {meta['qualities']} varian</p>")
    if meta.get("codec"):
        rows.append(f"<p>🎞 <b>Codec:</b> {meta['codec']}</p>")
    if meta.get("audio"):
        rows.append(f"<p>🔊 <b>Audio:</b> {meta['audio']}</p>")
    if not rows:
        return ""
    label = f"🎬 Metadata Video ({n_video} video)" if n_video > 1 else "🎬 Metadata Video"
    return f"<details><summary>{label}</summary>{''.join(rows)}</details>"


def _build_rich_card(data: dict) -> str:
    owner = data.get("owner", "-")
    full = data.get("full_name") or ""
    verified = " ✔️" if data.get("verified") else ""
    media = data.get("media") or []
    ts = data.get("timestamp")
    try:
        date_disp = datetime.fromtimestamp(int(ts)).strftime("%d %b %Y %H:%M")
    except Exception:
        date_disp = "-"

    parts: list = []
    slideshow = _build_slideshow(data)
    if slideshow:
        parts.append(slideshow)
    who = f"📸 <b>@{_esc(owner)}</b>{verified}"
    if full:
        who += f" · {_esc(full)}"
    parts.append(f"<p>{who}</p>")

    n_video = data.get("n_video", 0)
    media_label = f"{len(media)}"
    if len(media) > 1:
        media_label += " (carousel)"
    if n_video:
        media_label += f", {n_video} video"
    parts.append(
        "<table bordered striped>"
        f"<tr><td>❤️ Likes</td><td><b>{_fmt_num(data.get('likes', 0))}</b></td></tr>"
        f"<tr><td>💬 Komentar</td><td><b>{_fmt_num(data.get('comments', 0))}</b></td></tr>"
        f"<tr><td>🖼 Media</td><td><b>{media_label}</b></td></tr>"
        f"<tr><td>📅 Tanggal</td><td>{date_disp}</td></tr>"
        "</table>"
    )

    details = _build_video_details(data)
    if details:
        parts.append(details)

    caption = (data.get("caption") or "").strip()
    if caption:
        if len(caption) > MAX_CAPTION:
            caption = caption[:MAX_CAPTION] + "..."
        for para in caption.split("\n\n"):
            para = para.strip()
            if para:
                parts.append(f"<p>{_esc(para).replace(chr(10), '<br>')}</p>")
    return "".join(parts)


def _build_plain_card(data: dict) -> str:
    owner = data.get("owner", "-")
    verified = " ✔️" if data.get("verified") else ""
    media = data.get("media") or []
    n_video = data.get("n_video", 0)
    head = f"❤️ {_fmt_num(data.get('likes', 0))} • 💬 {_fmt_num(data.get('comments', 0))} • 🖼 {len(media)}"
    if n_video:
        head += f" ({n_video} video)"
    lines = [f"📸 <b>@{_esc(owner)}</b>{verified}", head]
    meta = data.get("video_meta") or {}
    if meta:
        bits = [f"{k}: {v}" for k, v in meta.items()]
        lines.append("🎬 " + " • ".join(bits))
    caption = (data.get("caption") or "").strip()
    if caption:
        if len(caption) > 900:
            caption = caption[:900] + "..."
        lines.append("")
        lines.append(_esc(caption))
    return "\n".join(lines)


def _url_keyboard(data: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔗 Buka di Instagram",
                    url=f"https://www.instagram.com/p/{data.get('shortcode', '')}/",
                )
            ]
        ]
    )


@app.on_message(filters.command(["igdl", "instadl"], COMMAND_HANDLER))
@capture_err
async def igdl_handler(client, message):
    if len(message.command) == 1:
        return await message.reply(
            f"<b>📸 Instagram Downloader</b>\n\n"
            f"Gunakan: <code>/{message.command[0]} &lt;link&gt;</code>\n\n"
            f"Contoh:\n"
            f"<code>/{message.command[0]} https://www.instagram.com/p/DcdCVwzkULZ/</code>"
        )

    link = message.command[1].strip()
    if not any(d in link for d in ("instagram.com", "instagr.am")):
        return await message.reply(
            "<b>❌</b> Link bukan dari Instagram. Harap berikan URL instagram.com."
        )

    status_msg = await message.reply(
        "<emoji id=5319190934510904031>⏳</emoji> <b>Processing Instagram post...</b>"
    )

    data = await _get_instagram_data(link)
    if not data.get("ok"):
        reason = data.get("reason", "unknown")
        if reason == "unavailable_or_private":
            err = (
                "<b>❌ Post tidak tersedia.</b>\n\n"
                "Kemungkinan post private / sudah dihapus.\n"
                "Untuk post private: taruh <code>cookies.txt</code> (format yt-dlp) "
                "di root project atau set <code>IG_COOKIES_FILE</code>, "
                "akun cookies harus follow akun post-nya."
            )
        elif reason == "rate_limited":
            err = "<b>❌ Rate limited oleh Instagram.</b> Coba lagi beberapa menit lagi."
        else:
            err = f"<b>❌ Gagal mengambil data Instagram.</b>\n<code>{reason}</code>"
        return await status_msg.edit(err)

    if not data.get("media"):
        return await status_msg.edit("<b>❌ Tidak ada media yang ditemukan.</b>")

    keyb = _url_keyboard(data)
    try:
        await status_msg.edit_rich(
            InputRichMessage(html=_build_rich_card(data)),
            reply_markup=keyb,
        )
    except Exception as e:
        LOGGER.warning("igdl edit rich gagal (%s): %s, fallback plain", e.__class__.__name__, e)
        try:
            await status_msg.edit(_build_plain_card(data), reply_markup=keyb)
        except Exception as e2:
            LOGGER.error("igdl edit plain gagal: %s", e2)


@app.on_message(filters.command(["twitterdl"], COMMAND_HANDLER))
@capture_err
async def twitterdl(_, message):
    if len(message.command) == 1:
        return await message.reply(
            f"Use command /{message.command[0]} [link] to download Twitter video."
        )
    url = message.command[1]
    if "x.com" in url:
        url = url.replace("x.com", "twitter.com")
    msg = await message.reply("<emoji id=5319190934510904031>⏳</emoji> Processing..")
    try:
        headers = {
            "Host": "ssstwitter.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "HX-Request": "true",
            "Origin": "https://ssstwitter.com",
            "Referer": "https://ssstwitter.com/id",
            "Cache-Control": "no-cache",
        }
        data = {
            "id": url,
            "locale": "id",
            "tt": "bc9841580b5d72e855e7d01bf3255278l",
            "ts": "1691416179",
            "source": "form",
        }
        post = await fetch.post(
            "https://ssstwitter.com/id",
            data=data,
            headers=headers,
            follow_redirects=True,
        )
        if post.status_code not in [200, 401]:
            return await msg.edit("Unknown error.")
        soup = BeautifulSoup(post.text, "lxml")
        cekdata = soup.find(
            "a",
            {
                "pure-button pure-button-primary is-center u-bl dl-button download_link without_watermark vignette_active"
            },
        )
        if not cekdata:
            return await message.reply(
                "ERROR: Oops! It seems that this tweet doesn't have a video! Try later or check your link"
            )
        try:
            fname = (
                (await fetch.head(cekdata.get("href")))
                .headers.get("content-disposition", "")
                .split("filename=")[1]
            )
            obj = SmartDL(cekdata.get("href"), progress_bar=False, timeout=15)
            obj.start()
            path = obj.get_dest()
            await message.reply_video(
                path,
                caption=f"<code>{fname}</code>\n\nUploaded for {message.from_user.mention} [<code>{message.from_user.id}</code>]",
            )
        except Exception as er:
            LOGGER.error("ERROR: while fetching TwitterDL. %s", er)
            return await msg.edit("ERROR: Got error while extracting link.")
        await msg.delete()
    except Exception as e:
        await message.reply(f"Failed to download twitter video..\n\n<b>Reason:</b> {e}")
        await msg.delete()


@app.on_message(filters.command(["tiktokdl"], COMMAND_HANDLER))
@capture_err
async def tiktokdl(_, message):
    if len(message.command) == 1:
        return await message.reply(
            f"Use command /{message.command[0]} [link] to download tiktok video."
        )
    link = message.command[1]
    msg = await message.reply("<emoji id=5319190934510904031>⏳</emoji> Processing..")
    try:
        r = (
            await fetch.post(
                "https://lovetik.com/api/ajax/search", data={"query": link}
            )
        ).json()
        fname = (await fetch.head(r["links"][0]["a"])).headers.get(
            "content-disposition", ""
        )
        filename = unquote(fname.split("filename=")[1].strip('"').split('"')[0])
        await message.reply_video(
            r["links"][0]["a"],
            caption=f"<b>Title:</b> <code>{filename}</code>\n<b>Uploader</b>: <a href='https://www.tiktok.com/{r['author']}'>{r['author_name']}</a>\n\nUploaded for {message.from_user.mention} [<code>{message.from_user.id}</code>]",
        )
        await msg.delete()
    except Exception as e:
        await message.reply(f"Failed to download tiktok video..\n\n<b>Reason:</b> {e}")
        await msg.delete()


def _fb_canonical(url: str) -> str:
    try:
        s = _session_with_cookies(("facebook.com", "fbcdn.net"))
        r = s.get(url, timeout=30, allow_redirects=True)
        return r.url
    except Exception:
        return url


def _fb_parse_count(text: str):
    m = re.match(r"([\d.,]+)\s*([KMkm])?", str(text or "").strip())
    if not m:
        return None
    try:
        n = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    unit = (m.group(2) or "").upper()
    if unit == "K":
        n *= 1000
    elif unit == "M":
        n *= 1000000
    return int(n)


_FB_FID_PREFIX = "ZmVlZGJhY2s6"


def _fb_decode_fid(fid: str) -> str:
    try:
        return base64.b64decode(fid + "==").decode("utf-8", "ignore")
    except Exception:
        return ""


def _fb_post_id(url: str) -> str:
    m = re.search(r"[?&]v=(\d+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/(?:permalink|posts|videos|reel)/(\d+)", url)
    return m.group(1) if m else ""


def _fb_collect_feed(obj, feeds, path="", depth=0):
    if depth > 45:
        return
    if isinstance(obj, dict):
        fid = obj.get("id")
        if isinstance(fid, str) and fid.startswith(_FB_FID_PREFIX):
            feeds.append((path, obj))
        for k, v in obj.items():
            _fb_collect_feed(v, feeds, f"{path}.{k}", depth + 1)
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            _fb_collect_feed(x, feeds, f"{path}[{i}]", depth + 1)


def _fb_feed_counts(feed: dict) -> dict:
    counts: dict = {}
    rc = feed.get("reaction_count")
    if isinstance(rc, dict):
        rc = rc.get("count")
    if isinstance(rc, int) and rc > 0:
        counts["reactions"] = rc
    tc = feed.get("total_comment_count")
    if isinstance(tc, int) and tc > 0:
        counts["comments"] = tc
    for key in ("share_count_reduced", "share_count"):
        sc = feed.get(key)
        if isinstance(sc, dict):
            sc = sc.get("count") or (sc.get("count") == 0 and 0)
        if isinstance(sc, str) and sc.strip().isdigit():
            sc = int(sc)
        if isinstance(sc, int) and sc > 0:
            counts["shares"] = sc
            break
    return counts


def _fb_feed_views(feed: dict):
    for key in ("video_view_count", "video_view_count_reduced", "play_count"):
        v = feed.get(key)
        if isinstance(v, dict):
            v = v.get("count")
        if isinstance(v, str) and v.strip().isdigit():
            v = int(v)
        if isinstance(v, int) and v > 0:
            return v
    return None


def _fb_pick_feed(feeds: list, post_id: str):
    best = None
    best_key = None
    for path, feed in feeds:
        fid = _fb_decode_fid(feed.get("id") or "")
        key = (
            int(bool(post_id) and post_id in fid),
            int(path.endswith(".result.data.feedback")),
            1 if feed.get("video_view_count_renderer") else 0,
            int((_fb_feed_counts(feed) or {}).get("reactions") or 0),
        )
        if best_key is None or key > best_key:
            best_key = key
            best = feed
    return best or {}


def _fb_find_node(obj, out, depth=0):
    if depth > 40:
        return
    if isinstance(obj, dict):
        if "post_id" in obj and "feedback" in obj:
            out.append(obj)
        for v in obj.values():
            _fb_find_node(v, out, depth + 1)
    elif isinstance(obj, list):
        for x in obj:
            _fb_find_node(x, out, depth + 1)


def _fb_find_key(obj, key, out, depth=0):
    if depth > 40:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                out.append(v)
            _fb_find_key(v, key, out, depth + 1)
    elif isinstance(obj, list):
        for x in obj:
            _fb_find_key(x, key, out, depth + 1)


def _fb_extract_media(node: dict) -> list:
    media: list = []
    seen = set()

    def add(url, mtype):
        if url and url not in seen:
            seen.add(url)
            media.append({"type": mtype, "url": url})

    vids: list = []
    for key in ("playable_url", "browser_native_hd_url", "browser_native_sd_url"):
        _fb_find_key(node.get("attachments"), key, vids)
    for v in vids:
        if isinstance(v, str) and v.startswith("http"):
            add(v, "video")

    for att in node.get("attachments") or []:
        styles = att.get("styles") or {}
        inner = styles.get("attachment") or att
        pm = (inner.get("media") or {}).get("photo_image")
        if isinstance(pm, dict) and pm.get("uri"):
            add(pm["uri"], "photo")

    if not media:
        uris: list = []
        _fb_find_key(node.get("attachments"), "uri", uris)
        for u in uris:
            if isinstance(u, str) and "scontent" in u:
                add(u, "photo")
    return media


def _fb_html_data(url: str) -> dict:
    for use_cookies in (True, False):
        s = _session_with_cookies(("facebook.com", "fbcdn.net"), use_cookies=use_cookies)
        try:
            r = s.get(url, timeout=30, allow_redirects=True, max_redirects=10)
        except Exception as e:
            LOGGER.warning(
                "fbdl request gagal (%s, cookie=%s): %s",
                e.__class__.__name__,
                use_cookies,
                str(e)[:90],
            )
            continue
        if r.status_code != 200:
            continue
        break
    else:
        return {"ok": False, "reason": "request_failed"}
    html = r.text
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
    nodes: list = []
    feeds: list = []
    for sc in scripts:
        sc = sc.strip()
        if not sc.startswith(("{", "[")):
            continue
        try:
            parsed = json.loads(sc)
        except Exception:
            continue
        _fb_find_node(parsed, nodes)
        _fb_collect_feed(parsed, feeds)
    if not nodes and not str(r.text).strip():
        return {"ok": False, "reason": "no_node"}

    final = str(r.url or url)
    cid = _fb_post_id(final)

    def _cap_len(n):
        sec = n.get("comet_sections") or {}
        story = (sec.get("content") or {}).get("story") or {}
        return len(((story.get("message") or {}).get("text") or ""))

    node = max(nodes, key=lambda n: (str(n.get("post_id") or "") == cid, _cap_len(n))) if nodes else {}
    feedback = node.get("feedback") or {}
    owner = feedback.get("owning_profile") or {}
    sections = node.get("comet_sections") or {}
    story = (sections.get("content") or {}).get("story") or {}
    message = (story.get("message") or {}).get("text") or ""

    feed = _fb_pick_feed(feeds, cid)
    counts = _fb_feed_counts(feed)
    views = _fb_feed_views(feed)

    return {
        "ok": True,
        "post_id": node.get("post_id") or cid,
        "owner": owner.get("name") or owner.get("short_name") or "",
        "caption": message,
        "timestamp": node.get("creation_time"),
        "media": _fb_extract_media(node),
        "counts": counts,
        "views": views,
        "n_attachments": len(node.get("attachments") or []),
        "permalink": node.get("permalink_url") or final,
        "cookies_used": bool(_resolve_cookies_path()),
    }


def _fb_ytdlp(url: str) -> dict:
    def _run():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "socket_timeout": 30,
        }
        opts.update(_ydl_cookie_opts())
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = _run()
    except Exception as e:
        LOGGER.info("fbdl yt-dlp gagal (%s): %s", e.__class__.__name__, str(e)[:120])
        return {}

    fmts = info.get("formats") or []
    video_fmts = [f for f in fmts if f.get("vcodec") and f["vcodec"] != "none"]
    h = [f for f in video_fmts if f.get("height")]
    best = max(h, key=lambda f: f.get("height") or 0) if h else None

    title = info.get("title") or ""
    views = info.get("view_count")
    reactions = None
    m = re.search(r"([\d.,]+[KkMm]?)\s*reactions", title, re.I)
    if m:
        reactions = _fb_parse_count(m.group(1))
    elif "likes" in title.lower():
        m2 = re.search(r"([\d.,]+[KkMm]?)\s*(?:likes|suka)", title, re.I)
        if m2:
            reactions = _fb_parse_count(m2.group(1))
    views = views or _fb_parse_count(re.search(r"([\d.,]+[KkMm]?)\s*views", title, re.I).group(1)) if re.search(r"([\d.,]+[KkMm]?)\s*views", title, re.I) else views

    meta = {}
    dur = info.get("duration")
    if dur:
        meta["duration"] = _parse_duration(dur)
    if best:
        meta["resolution"] = f"{best.get('width')}x{best.get('height')}"
    if video_fmts:
        meta["qualities"] = str(len(video_fmts))
        codecs = sorted({(f.get("vcodec") or "").split(".")[0] for f in video_fmts if f.get("vcodec")})
        if codecs:
            meta["codec"] = ", ".join(codecs)

    return {
        "title": title,
        "uploader": info.get("uploader") or "",
        "caption": info.get("description") or "",
        "duration": info.get("duration"),
        "view_count": views,
        "reactions": reactions,
        "media_url": (best or {}).get("url") or info.get("url"),
        "thumb": info.get("thumbnail"),
        "meta": meta or None,
        "is_video": bool(video_fmts),
    }


def _fb_extract_sync(url: str) -> dict:
    if not cffi_requests:
        return {"ok": False, "reason": "no_curl_cffi"}

    canon = _fb_canonical(url)
    data = _fb_html_data(canon)

    yt = _fb_ytdlp(canon)

    if not data.get("ok") and not yt:
        raw = _fb_html_data(url)
        if raw.get("ok"):
            data = raw
        else:
            code = re.search(r"/(?:reel|videos|watch)/(\d+)", canon)
            if code:
                yt2 = _fb_ytdlp(f"https://www.facebook.com/watch/?v={code.group(1)}")
                if yt2:
                    yt = yt2
    if not data.get("ok") and not yt:
        return {"ok": False, "reason": data.get("reason") or "no_data"}

    media = list(data.get("media") or []) if data.get("ok") else []
    if yt.get("media_url"):
        media = [m for m in media if m["type"] != "photo" or m["url"] != yt.get("thumb")]
        if (data.get("n_attachments") or 0) <= 1:
            media = [m for m in media if m["type"] != "photo"]
        media.insert(0, {"type": "video", "url": yt["media_url"]})
    if not media and yt.get("thumb"):
        media = [{"type": "photo", "url": yt["thumb"]}]

    caption = (data.get("caption") if data.get("ok") else "") or yt.get("caption") or ""
    owner = (data.get("owner") if data.get("ok") else "") or yt.get("uploader") or "Facebook"
    ts = data.get("timestamp") if data.get("ok") else None

    counts = dict(data.get("counts") or {})
    if yt.get("reactions") and "reactions" not in counts:
        counts["reactions"] = yt["reactions"]

    return {
        "ok": True,
        "platform": "Facebook",
        "owner": owner,
        "caption": caption,
        "timestamp": ts,
        "media": media,
        "counts": counts,
        "views": data.get("views") or yt.get("view_count"),
        "video_meta": yt.get("meta"),
        "n_video": sum(1 for x in media if x["type"] == "video"),
        "shortcode": str(data.get("post_id") or "") or "",
        "permalink": data.get("permalink") or canon,
        "title": yt.get("title") or "",
        "cookies_used": bool(data.get("cookies_used")),
    }


async def _get_facebook_data(link: str) -> dict:
    try:
        return await asyncio.to_thread(_fb_extract_sync, link)
    except Exception as e:
        LOGGER.warning("fbdl extract gagal: %s", e)
        return {"ok": False, "reason": f"exception:{e.__class__.__name__}"}


def _fb_rich_card(data: dict) -> str:
    owner = data.get("owner") or "Facebook"
    media = data.get("media") or []
    counts = data.get("counts") or {}
    ts = data.get("timestamp")
    try:
        date_disp = datetime.fromtimestamp(int(ts)).strftime("%d %b %Y %H:%M")
    except Exception:
        date_disp = "-"

    parts: list = []
    if media:
        items = []
        for item in media[:MAX_MEDIA]:
            src = _esc(item["url"])
            items.append(f'<video src="{src}"/>' if item["type"] == "video" else f'<img src="{src}"/>')
        label = f"{len(media)} media" if len(media) > 1 else "1 media"
        parts.append(f"<tg-slideshow>{''.join(items)}<figcaption>{_esc(owner)} · {label}</figcaption></tg-slideshow>")

    parts.append(f"<p>📘 <b>{_esc(owner)}</b></p>")

    rows = []
    if "reactions" in counts:
        rows.append(f"<tr><td>👍 Reaksi</td><td><b>{_fmt_num(counts['reactions'])}</b></td></tr>")
    if "comments" in counts:
        rows.append(f"<tr><td>💬 Komentar</td><td><b>{_fmt_num(counts['comments'])}</b></td></tr>")
    if "shares" in counts:
        rows.append(f"<tr><td>🔁 Dibagikan</td><td><b>{_fmt_num(counts['shares'])}</b></td></tr>")
    if data.get("views"):
        rows.append(f"<tr><td>👁 Tayangan</td><td><b>{_fmt_num(data['views'])}</b></td></tr>")
    rows.append(f"<tr><td>🖼 Media</td><td><b>{len(media)}</b></td></tr>")
    if date_disp != "-":
        rows.append(f"<tr><td>📅 Tanggal</td><td>{date_disp}</td></tr>")
    if not any(k in counts for k in ("reactions", "comments", "shares")):
        hint = (
            "0 / tidak terlihat oleh akun ini"
            if data.get("cookies_used")
            else "perlu cookies.txt (login)"
        )
        rows.append(f"<tr><td>📊 Metrik</td><td>{hint}</td></tr>")
    parts.append("<table bordered striped>" + "".join(rows) + "</table>")

    meta = data.get("video_meta")
    if meta:
        mrows = []
        if meta.get("duration"):
            mrows.append(f"<p>⏱ <b>Durasi:</b> {meta['duration']}</p>")
        if meta.get("resolution"):
            mrows.append(f"<p>📐 <b>Resolusi:</b> {meta['resolution']}</p>")
        if meta.get("qualities"):
            mrows.append(f"<p>🎚 <b>Kualitas:</b> {meta['qualities']} varian</p>")
        if meta.get("codec"):
            mrows.append(f"<p>🎞 <b>Codec:</b> {meta['codec']}</p>")
        if mrows:
            parts.append(f"<details><summary>🎬 Metadata Video</summary>{''.join(mrows)}</details>")

    caption = (data.get("caption") or "").strip()
    if caption:
        if len(caption) > MAX_CAPTION:
            caption = caption[:MAX_CAPTION] + "..."
        for para in caption.split("\n\n"):
            para = para.strip()
            if para:
                parts.append(f"<p>{_esc(para).replace(chr(10), '<br>')}</p>")
    return "".join(parts)


def _fb_plain_card(data: dict) -> str:
    counts = data.get("counts") or {}
    bits = []
    if "reactions" in counts:
        bits.append(f"👍 {_fmt_num(counts['reactions'])}")
    if "comments" in counts:
        bits.append(f"💬 {_fmt_num(counts['comments'])}")
    if data.get("views"):
        bits.append(f"👁 {_fmt_num(data['views'])}")
    bits.append(f"🖼 {len(data.get('media') or [])}")
    lines = [f"📘 <b>{_esc(data.get('owner') or 'Facebook')}</b>", " • ".join(bits)]
    caption = (data.get("caption") or "").strip()
    if caption:
        if len(caption) > 900:
            caption = caption[:900] + "..."
        lines.append("")
        lines.append(_esc(caption))
    return "\n".join(lines)


def _fb_keyboard(data: dict) -> InlineKeyboardMarkup:
    url = data.get("permalink") or "https://www.facebook.com"
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Buka di Facebook", url=url)]])


@app.on_message(filters.command(["fbdl", "fb"], COMMAND_HANDLER))
@capture_err
async def fbdl(_, message):
    if len(message.command) == 1:
        return await message.reply(
            f"Gunakan: <code>/{message.command[0]} &lt;link&gt;</code>\n\n"
            f"Contoh:\n<code>/{message.command[0]} https://www.facebook.com/share/p/18qRpLjJEk/</code>"
        )

    link = message.command[1].strip()
    if not any(d in link for d in ("facebook.com", "fb.watch", "fb.me")):
        return await message.reply("<b>❌</b> Link bukan dari Facebook.")

    status_msg = await message.reply(
        "<emoji id=5319190934510904031>⏳</emoji> <b>Processing Facebook post...</b>"
    )

    data = await _get_facebook_data(link)
    if not data.get("ok") or not data.get("media"):
        return await status_msg.edit(
            "<b>❌ Gagal mengambil data Facebook.</b>\n\n"
            "Kemungkinan: post private / grup tertutup / link butuh login.\n"
            f"<code>{data.get('reason', 'no_media')}</code>"
        )

    keyb = _fb_keyboard(data)
    try:
        await status_msg.edit_rich(InputRichMessage(html=_fb_rich_card(data)), reply_markup=keyb)
    except Exception as e:
        LOGGER.warning("fbdl rich gagal (%s): %s, fallback plain", e.__class__.__name__, e)
        try:
            await status_msg.edit(_fb_plain_card(data), reply_markup=keyb)
        except Exception as e2:
            LOGGER.error("fbdl plain gagal: %s", e2)
