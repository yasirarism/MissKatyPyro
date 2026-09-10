import asyncio
import time
from datetime import datetime
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from misskaty.helper.sosmed_common import (
    _session_with_cookies,
    _esc,
    cffi_requests,
    MAX_MEDIA,
    MAX_CAPTION,
    LOGGER,
)


TT_API = "https://www.tikwm.com/api/"


TT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def _tt_fmt_num(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "0"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}jt".replace(".0jt", "jt")
    if n >= 1_000:
        return f"{n / 1_000:.1f}rb".replace(".0rb", "rb")
    return str(n)


def _tt_duration(seconds) -> str:
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return ""
    if total <= 0:
        return ""
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def _tt_extract_sync(link: str) -> dict:
    if not cffi_requests:
        return {"ok": False, "reason": "no_curl_cffi"}

    params = {"url": link, "hd": "1"}
    last_msg = ""
    for attempt in range(3):
        s = _session_with_cookies(use_cookies=False)
        s.headers.update({"User-Agent": TT_UA, "Referer": "https://www.tiktok.com/"})
        try:
            r = s.get(TT_API, params=params, timeout=30)
        except Exception as e:
            LOGGER.warning("tiktok request gagal (%s): %s", e.__class__.__name__, str(e)[:90])
            return {"ok": False, "reason": "request_failed"}
        if r.status_code != 200:
            return {"ok": False, "reason": f"http_{r.status_code}"}
        try:
            payload = r.json()
        except Exception:
            return {"ok": False, "reason": "bad_json"}

        code = payload.get("code")
        if code == 0:
            break
        last_msg = str(payload.get("msg") or "")
        if "limit" in last_msg.lower() and attempt < 2:
            time.sleep(1.4)
            continue
        return {"ok": False, "reason": "unavailable" if code == -1 else "api_error", "detail": last_msg}
    else:
        return {"ok": False, "reason": "rate_limited", "detail": last_msg}

    d = payload.get("data") or {}
    if not d:
        return {"ok": False, "reason": "no_data"}

    author = d.get("author") or {}
    music = d.get("music_info") or {}

    media: list = []
    images = d.get("images") or []
    for img in images:
        if isinstance(img, str) and img:
            media.append({"type": "photo", "url": img})
    if not media:
        video_url = d.get("hdplay") or d.get("play") or d.get("wmplay")
        cover = d.get("origin_cover") or d.get("cover") or (author.get("avatar"))
        if video_url:
            media.append({"type": "video", "url": video_url, "cover": cover})

    meta = {}
    dur = _tt_duration(d.get("duration"))
    if dur:
        meta["duration"] = dur
    if d.get("hd_size"):
        meta["size_hd"] = f"{int(d['hd_size']) / 1048576:.1f} MB"
    elif d.get("size"):
        meta["size"] = f"{int(d['size']) / 1048576:.1f} MB"
    if d.get("music_info"):
        if music.get("title"):
            meta["music"] = music["title"]
        if music.get("author"):
            meta["music_author"] = music["author"]
    if d.get("is_ad"):
        meta["iklan"] = "ya"

    return {
        "ok": True,
        "platform": "TikTok",
        "id": str(d.get("id") or ""),
        "owner": author.get("nickname") or author.get("unique_id") or "TikTok",
        "username": author.get("unique_id") or "",
        "verified": bool(author.get("verified")),
        "avatar": author.get("avatar") or "",
        "caption": d.get("title") or "",
        "timestamp": d.get("create_time"),
        "media": media,
        "counts": {
            "views": d.get("play_count"),
            "likes": d.get("digg_count"),
            "comments": d.get("comment_count"),
            "shares": d.get("share_count"),
            "saves": d.get("collect_count"),
        },
        "video_meta": meta or None,
        "permalink": f"https://www.tiktok.com/@{author.get('unique_id')}/video/{d.get('id')}"
        if author.get("unique_id") and d.get("id")
        else "",
        "music_url": (music.get("play") or ""),
    }


def _tt_rich_card(data: dict) -> str:
    owner = data.get("owner") or "TikTok"
    username = data.get("username") or ""
    verified = " ✔️" if data.get("verified") else ""
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
        parts.append(
            f"<tg-slideshow>{''.join(items)}"
            f"<figcaption>@{_esc(username) or _esc(owner)} · {label}</figcaption></tg-slideshow>"
        )

    parts.append(f"<p>🎵 <b>{_esc(owner)}</b>{verified}</p>")

    rows = []
    if counts.get("views"):
        rows.append(f"<tr><td>👁 Tayangan</td><td><b>{_tt_fmt_num(counts['views'])}</b></td></tr>")
    if counts.get("likes"):
        rows.append(f"<tr><td>❤️ Suka</td><td><b>{_tt_fmt_num(counts['likes'])}</b></td></tr>")
    if counts.get("comments"):
        rows.append(f"<tr><td>💬 Komentar</td><td><b>{_tt_fmt_num(counts['comments'])}</b></td></tr>")
    if counts.get("shares"):
        rows.append(f"<tr><td>🔁 Dibagikan</td><td><b>{_tt_fmt_num(counts['shares'])}</b></td></tr>")
    if counts.get("saves"):
        rows.append(f"<tr><td>🔖 Disimpan</td><td><b>{_tt_fmt_num(counts['saves'])}</b></td></tr>")
    rows.append(f"<tr><td>🖼 Media</td><td><b>{len(media)}</b></td></tr>")
    if date_disp != "-":
        rows.append(f"<tr><td>📅 Tanggal</td><td>{date_disp}</td></tr>")
    if username:
        rows.append(f"<tr><td>👤 Akun</td><td>@{_esc(username)}</td></tr>")
    parts.append("<table bordered striped>" + "".join(rows) + "</table>")

    meta = data.get("video_meta")
    if meta:
        labels = {
            "duration": ("⏱", "Durasi"),
            "size": ("💾", "Ukuran"),
            "size_hd": ("💾", "Ukuran HD"),
            "music": ("🎵", "Musik"),
            "music_author": ("🎤", "Artis"),
            "iklan": ("📢", "Iklan"),
        }
        mrows = []
        for key, (icon, label) in labels.items():
            if meta.get(key):
                mrows.append(f"<p>{icon} <b>{label}:</b> {_esc(str(meta[key]))}</p>")
        if mrows:
            parts.append(f"<details><summary>🎬 Metadata</summary>{''.join(mrows)}</details>")

    caption = (data.get("caption") or "").strip()
    if caption:
        if len(caption) > MAX_CAPTION:
            caption = caption[:MAX_CAPTION] + "..."
        for para in caption.split("\n\n"):
            para = para.strip()
            if para:
                parts.append(f"<p>{_esc(para).replace(chr(10), '<br>')}</p>")
    return "".join(parts)


def _tt_plain_card(data: dict) -> str:
    counts = data.get("counts") or {}
    bits = []
    if counts.get("views"):
        bits.append(f"👁 {_tt_fmt_num(counts['views'])}")
    if counts.get("likes"):
        bits.append(f"❤️ {_tt_fmt_num(counts['likes'])}")
    if counts.get("comments"):
        bits.append(f"💬 {_tt_fmt_num(counts['comments'])}")
    lines = [f"🎵 <b>{_esc(data.get('owner') or 'TikTok')}</b>", " • ".join(bits) or "—"]
    meta = data.get("video_meta") or {}
    if meta:
        lines.append("🎬 " + " • ".join(f"{k}: {v}" for k, v in meta.items()))
    caption = (data.get("caption") or "").strip()
    if caption:
        if len(caption) > 900:
            caption = caption[:900] + "..."
        lines.append("")
        lines.append(_esc(caption))
    return "\n".join(lines)


def _tt_keyboard(data: dict) -> InlineKeyboardMarkup:
    link = data.get("permalink") or "https://www.tiktok.com"
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Buka di TikTok", url=link)]])


async def _get_tiktok_data(link: str) -> dict:
    return await asyncio.to_thread(_tt_extract_sync, link)
