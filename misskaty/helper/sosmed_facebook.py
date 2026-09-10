import asyncio
import base64
import json
import re
from datetime import datetime
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from misskaty.helper.sosmed_common import (
    _resolve_cookies_path,
    _session_with_cookies,
    _ydl_cookie_opts,
    _fmt_num,
    _esc,
    _parse_duration,
    cffi_requests,
    YoutubeDL,
    MAX_MEDIA,
    MAX_CAPTION,
    LOGGER,
)


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
