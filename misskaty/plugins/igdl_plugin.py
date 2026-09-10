import asyncio
import json
import logging
import os
import re
from datetime import datetime
from urllib.parse import urlparse

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputRichMessage

from misskaty import app
from misskaty.core.decorator import capture_err
from misskaty.vars import COMMAND_HANDLER

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

LOGGER = logging.getLogger("MissKaty")

__MODULE__ = "InstagramDL"
__HELP__ = """
/igdl [link] - Tampilkan Instagram post/reel sebagai slideshow dalam satu rich message (media + likes + komentar + caption + metadata video).
Contoh: /igdl https://www.instagram.com/p/DcdCVwzkULZ/

Post private? Taruh file cookies.txt (format Netscape/yt-dlp) di root project
atau set env IG_COOKIES_FILE=/path/cookies.txt, akun cookies harus follow akun post-nya.
"""

COOKIES_ENV = os.environ.get("IG_COOKIES_FILE")
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
    if COOKIES_ENV and os.path.exists(COOKIES_ENV):
        return COOKIES_ENV
    if os.path.exists(COOKIES_DEFAULT):
        return COOKIES_DEFAULT
    return None


def _load_netscape_cookies(path: str) -> dict:
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
                if "instagram.com" in domain:
                    cookies[name] = value
    except Exception as e:
        LOGGER.warning("igdl gagal baca cookies.txt (%s): %s", path, e.__class__.__name__)
    return cookies


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

    s = cffi_requests.Session(impersonate="chrome")
    cookies_path = _resolve_cookies_path()
    if cookies_path:
        cookies = _load_netscape_cookies(cookies_path)
        if cookies:
            s.cookies.update(cookies)
            LOGGER.info("igdl pakai cookies.txt (%d cookie IG)", len(cookies))

    r = s.get(f"https://www.instagram.com/p/{shortcode}/", timeout=30)
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
        parts.append("<br>")
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


@app.on_message(filters.command(["igdl"], COMMAND_HANDLER))
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
