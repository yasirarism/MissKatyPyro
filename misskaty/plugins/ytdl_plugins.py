# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import contextlib
from html import escape
from io import BytesIO
import os
from pathlib import Path
from time import time
from uuid import uuid4

from PIL import Image
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    MessageIdInvalid,
    MessageNotModified,
    QueryIdInvalid,
    WebpageMediaEmpty,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from yt_dlp import DownloadError, YoutubeDL

from misskaty import app
from misskaty.core import pyro_cooldown
from misskaty.core.decorator import capture_err, new_task
from misskaty.helper import (
    PROCESS_TEXT,
    dl_caption_meta,
    dl_finalizing_text,
    dl_progress_text,
    fetch,
    format_progress_bar,
    isValidURL,
    use_chat_lang,
)
from misskaty.helper.pyro_progress import humanbytes, time_formatter
from misskaty.vars import COMMAND_HANDLER

YT_REGEX = r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
YT_DB = {}
YTDL_CACHE = {}
ACTIVE_DOWNLOADS = {}


class DownloadCancelled(Exception):
    pass


def rand_key() -> str:
    return str(uuid4())[:8]


def _resolve_yt_url(ctx: Message) -> str:
    """Ambil URL untuk /ytdown.

    Prioritas: 1) argumen command, 2) reply message (text/caption),
    3) trigger regex (link dikirim langsung di chat). Mengembalikan string
    kosong kalau tidak ada URL sama sekali.
    """
    if ctx.command and len(ctx.command) > 1:
        return ctx.command[1]
    if ctx.reply_to_message:
        return (ctx.reply_to_message.text or ctx.reply_to_message.caption or "").strip()
    if ctx.command:
        return ""  # command tanpa argumen & tanpa reply
    return (ctx.text or ctx.caption or "").strip()


def get_cookie_file() -> str | None:
    configured_cookie = os.getenv("YTDL_COOKIE_FILE")
    if configured_cookie:
        cookie_file = Path(configured_cookie).expanduser()
        return str(cookie_file) if cookie_file.is_file() else None

    cookie_file = Path("cookies.txt")
    return str(cookie_file) if cookie_file.is_file() else None


def build_ydl_opts(extra: dict | None = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"deno": {"path": "/root/.deno/bin/deno"}},
        "socket_timeout": 20,
        "retries": 1,
    }
    if cookie_file := get_cookie_file():
        opts["cookiefile"] = cookie_file
    if extra:
        opts.update(extra)
    return opts




def format_ytdl_error(err: Exception) -> str:
    msg = str(err).strip()
    if msg.startswith("ERROR: "):
        msg = msg[7:]
    return escape(msg)


def resolve_downloaded_file(output_dir: str, job_id: str, expected_ext: str | None = None) -> str | None:
    candidates = sorted(Path(output_dir).glob("*" if not job_id else f"{job_id}.*"), key=lambda x: x.stat().st_mtime, reverse=True)
    if expected_ext:
        for file in candidates:
            if file.suffix.lower() == f".{expected_ext.lower()}":
                return str(file)
    return str(candidates[0]) if candidates else None




def estimate_audio_size(duration: int, bitrate_kbps: int) -> int:
    if duration <= 0 or bitrate_kbps <= 0:
        return 0
    return int((duration * bitrate_kbps * 1000) / 8)


def parse_quality_tree(info: dict) -> dict:
    formats = info.get("formats") or []
    duration = int(info.get("duration") or 0)
    resolutions = {}

    heights = sorted({int(f.get("height") or 0) for f in formats if int(f.get("height") or 0) > 0}, reverse=True)
    for target_height in heights:
        candidates = []
        for fmt in formats:
            height = int(fmt.get("height") or 0)
            if height != target_height:
                continue
            if fmt.get("vcodec") in (None, "none"):
                continue
            vcodec = (fmt.get("vcodec") or "").lower()
            is_avc = vcodec.startswith("avc1") or "h264" in vcodec
            tbr = int(fmt.get("tbr") or fmt.get("vbr") or 0)
            fps = int(fmt.get("fps") or 0)
            format_id = str(fmt.get("format_id"))
            selector = format_id
            if fmt.get("acodec") in (None, "none"):
                # Gabung dengan audio AAC kalau tersedia (fallback bestaudio)
                selector = f"{format_id}+bestaudio[acodec^=mp4a]/bestaudio/best"
            size_bytes = int(fmt.get("filesize") or fmt.get("filesize_approx") or 0)
            candidates.append(
                {
                    "label": f"{tbr}kbps" if tbr else "Auto bitrate",
                    "format": selector,
                    "bitrate": tbr,
                    "kind": "video",
                    "ext": "mp4",
                    "size": size_bytes,
                    "fps": fps,
                    "format_id": format_id,
                    "height": target_height,
                    "codec": "AVC" if is_avc else (vcodec.split(".")[0].upper() or "?"),
                    "avc": is_avc,
                }
            )
        if candidates:
            # Prioritaskan H.264/AVC (kompatibel & ringan), lalu bitrate & fps
            resolutions[str(target_height)] = sorted(
                candidates,
                key=lambda x: (
                    not x.get("avc", False),
                    -x.get("bitrate", 0),
                    -x.get("fps", 0),
                ),
            )

    audio = []
    for bitrate in (320, 256, 192, 160, 128, 96, 64):
        audio.append(
            {
                "label": f"{bitrate}kbps",
                # AAC (m4a) dulu; fallback bestaudio kalau tidak tersedia
                "format": "bestaudio[acodec^=mp4a]/bestaudio/best",
                "kind": "audio",
                "ext": "m4a",
                "codec": "aac",
                "bitrate": str(bitrate),
                "size": estimate_audio_size(duration, bitrate),
            }
        )
    return {"resolutions": resolutions, "audio": audio}


async def animate_processing(message: Message, title: str, stop_event: asyncio.Event):
    frames = ["😺", "😸", "😹", "😻"]
    idx = 0
    while not stop_event.is_set():
        text = f"{frames[idx % len(frames)]} {title}"
        try:
            if message.media:
                await message.edit_caption(text, parse_mode=ParseMode.HTML)
            else:
                await message.edit_text(text, parse_mode=ParseMode.HTML)
        except Exception:
            pass
        idx += 1
        await asyncio.sleep(1.2)


async def yt_extract(url: str, flat: bool = False, timeout: int = 45) -> dict:
    def _extract():
        opts = build_ydl_opts({"skip_download": True})
        if flat:
            opts["extract_flat"] = "in_playlist"
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    return await asyncio.wait_for(asyncio.to_thread(_extract), timeout=timeout)


async def download_thumb_file(url: str | None, job_id: str, output_dir: str) -> str | None:
    if not url:
        return None
    try:
        response = await fetch.get(url)
        if response.status_code != 200:
            return None

        thumb_path = os.path.join(output_dir, f"{job_id}_thumb.jpg")
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.thumbnail((1280, 1280))
        image.save(thumb_path, format="JPEG", quality=85)
        if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
            return thumb_path
        return None
    except Exception:
        return None


async def generate_thumb_with_ffmpeg(video_file: str, job_id: str, output_dir: str) -> str | None:
    thumb_path = os.path.join(output_dir, f"{job_id}_thumb.jpg")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_file,
        "-vf",
        "thumbnail,scale=640:-1",
        "-frames:v",
        "1",
        thumb_path,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode == 0 and os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return thumb_path

    # fallback for very short or odd videos
    cmd_fallback = [
        "ffmpeg",
        "-y",
        "-ss",
        "00:00:00.200",
        "-i",
        video_file,
        "-frames:v",
        "1",
        thumb_path,
    ]
    process_fb = await asyncio.create_subprocess_exec(
        *cmd_fallback,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process_fb.communicate()
    if process_fb.returncode == 0 and os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return thumb_path
    return None


def quality_markup(cache_key: str, tree: dict) -> InlineKeyboardMarkup:
    rows = []
    for idx, (res, items) in enumerate(tree["resolutions"].items()):
        size_hint = next((x.get("size", 0) for x in items if x.get("size", 0) > 0), 0)
        label = f"🎬 {res}p" + (" ⭐" if idx == 0 else "")
        if size_hint:
            label += f" ({humanbytes(size_hint)})"
        rows.append([InlineKeyboardButton(label, callback_data=f"yt_res|{cache_key}|{res}")])
    rows.append([InlineKeyboardButton("🎧 Audio AAC", callback_data=f"yt_audio|{cache_key}")])
    return InlineKeyboardMarkup(rows)


@app.on_cmd("ytsearch", no_channel=True)
@use_chat_lang()
async def ytsearch(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply(strings("no_query"))
    query = ctx.text.split(maxsplit=1)[1]
    search_key = rand_key()
    search = await yt_extract(f"ytsearch10:{query}", flat=True)
    results = search.get("entries") or []
    if not results:
        return await ctx.reply(strings("no_res").format(kweri=query))
    YT_DB[search_key] = {"query": query, "results": results, "user_id": ctx.from_user.id}
    i = results[0]
    out = strings("yts_msg").format(
        pub=i.get("upload_date") or "-",
        dur=time_formatter(i.get("duration") or 0),
        vi=humanbytes(i.get("view_count") or 0),
        clink=i.get("channel_url") or i.get("uploader_url") or "https://youtube.com",
        cname=i.get("channel") or i.get("uploader") or "Unknown",
    )
    btn = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"1/{len(results)}", callback_data=f"ytdl_scroll|{search_key}|0")],
            [InlineKeyboardButton(strings("dl_btn"), callback_data=f"yt_gen|{search_key}|0")],
        ]
    )
    await ctx.reply_photo(await get_ytthumb(i.get("id")), caption=out, reply_markup=btn, parse_mode=ParseMode.HTML)


@app.on_message(
    filters.command(["ytdown"], COMMAND_HANDLER)
    | filters.regex(YT_REGEX)
    & ~filters.channel
    & ~filters.via_bot
    & pyro_cooldown.wait(60)
)
@capture_err
@use_chat_lang()
async def ytdownv2(_, ctx: Message, strings):
    if not ctx.from_user:
        return await ctx.reply(strings("no_channel"))
    # Tanpa URL (argumen/reply/teks) -> perintah ditolak, tidak memproses.
    url = _resolve_yt_url(ctx)
    if not url or not isValidURL(url):
        return await ctx.reply(strings("invalid_link"))

    progress_msg = await ctx.reply(PROCESS_TEXT, parse_mode=ParseMode.HTML)
    stop_event = asyncio.Event()
    anim_task = asyncio.create_task(animate_processing(progress_msg, PROCESS_TEXT, stop_event))
    try:
        info = await yt_extract(url)
    except DownloadError as err:
        return await progress_msg.edit_text(f"<code>{format_ytdl_error(err)}</code>", parse_mode=ParseMode.HTML)
    except asyncio.TimeoutError:
        return await progress_msg.edit_text("❌ Request timed out while contacting yt-dlp source.")
    except Exception as err:
        return await progress_msg.edit_text(
            f"{strings('err_parse')}\n\n<code>{format_ytdl_error(err)}</code>",
            parse_mode=ParseMode.HTML,
        )
    finally:
        stop_event.set()
        await anim_task

    cache_key = rand_key()
    tree = parse_quality_tree(info)
    YTDL_CACHE[cache_key] = {
        "url": url,
        "title": info.get("title") or "Untitled",
        "thumb": info.get("thumbnail") or "assets/thumb.jpg",
        "duration": int(info.get("duration") or 0),
        "uploader": info.get("uploader") or info.get("channel") or "",
        "artist": info.get("artist") or info.get("creator") or "",
        "album": info.get("album") or "",
        "track": info.get("track") or info.get("title") or "",
        "release_date": info.get("release_date") or info.get("upload_date") or "",
        "quality_tree": tree,
        "user_id": ctx.from_user.id,
    }

    caption = f"<b>{YTDL_CACHE[cache_key]['title']}</b>\n\n1) Select resolution\n2) Select bitrate"
    markup = quality_markup(cache_key, tree)
    try:
        await progress_msg.edit_media(
            InputMediaPhoto(YTDL_CACHE[cache_key]["thumb"], caption=caption, parse_mode=ParseMode.HTML),
            reply_markup=markup,
        )
    except WebpageMediaEmpty:
        await progress_msg.edit_media(
            InputMediaPhoto("assets/thumb.jpg", caption=caption, parse_mode=ParseMode.HTML),
            reply_markup=markup,
        )


@app.on_callback_query(filters.regex(r"^yt_(res|audio)\|"))
@use_chat_lang()
async def ytdl_pick_step(_, cq: CallbackQuery, strings):
    callback = cq.data.split("|")
    action, cache_key = callback[0], callback[1]
    data = YTDL_CACHE.get(cache_key)
    if not data:
        return await cq.answer("Task expired", show_alert=True)
    if cq.from_user.id != data["user_id"]:
        return await cq.answer(strings("unauth"), True)

    if action == "yt_res":
        res = callback[2]
        options = data["quality_tree"]["resolutions"].get(res, [])
        if not options:
            return await cq.answer("No bitrate option for this resolution", show_alert=True)
        rows = []
        for idx, opt in enumerate(options):
            fmt_id = opt.get("format_id") or "-"
            fps = opt.get("fps") or 0
            codec = opt.get("codec") or "?"
            label = f"{opt['label']} • {codec} • {fps}fps • {fmt_id}"
            if opt.get("size"):
                label += f" • {humanbytes(opt['size'])}"
            rows.append([InlineKeyboardButton(label, callback_data=f"yt_dl|{cache_key}|v|{res}|{idx}")])
        rows.append([InlineKeyboardButton("⬅️ Back", callback_data=f"yt_back|{cache_key}")])
        return await cq.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(rows))

    rows = []
    for opt in data["quality_tree"]["audio"]:
        label = f"🎧 {opt['label']}"
        if opt.get("size"):
            label += f" • {humanbytes(opt['size'])}"
        rows.append([InlineKeyboardButton(label, callback_data=f"yt_dl|{cache_key}|a|{opt['bitrate']}")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data=f"yt_back|{cache_key}")])
    await cq.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(rows))


@app.on_callback_query(filters.regex(r"^yt_back\|"))
@use_chat_lang()
async def ytdl_back_choice(_, cq: CallbackQuery, strings):
    cache_key = cq.data.split("|")[1]
    data = YTDL_CACHE.get(cache_key)
    if not data:
        return await cq.answer("Task expired", show_alert=True)
    if cq.from_user.id != data["user_id"]:
        return await cq.answer(strings("unauth"), True)
    await cq.edit_message_reply_markup(reply_markup=quality_markup(cache_key, data["quality_tree"]))


@app.on_callback_query(filters.regex(r"^yt_dl\|"))
@use_chat_lang()
@new_task
async def ytdl_download_callback(self: Client, cq: CallbackQuery, strings):
    callback = cq.data.split("|")
    cache_key = callback[1]
    data = YTDL_CACHE.get(cache_key)
    if not data:
        return await cq.answer("Task expired", show_alert=True)
    if cq.from_user.id != data["user_id"]:
        return await cq.answer(strings("unauth"), True)

    if callback[2] == "v":
        res = callback[3]
        idx = int(callback[4])
        option = data["quality_tree"]["resolutions"][res][idx]
        label = f"{res}p • {option['label']}"
    else:
        bitrate = callback[3]
        option = {"kind": "audio", "ext": "m4a", "codec": "aac", "format": "bestaudio/best", "bitrate": bitrate}
        label = f"AAC {bitrate}kbps"

    job_id = rand_key()
    requester = cq.from_user
    mention = requester.mention if requester else "Unknown"
    ACTIVE_DOWNLOADS[job_id] = {
        "cancelled": False,
        "downloaded": 0,
        "total": 0,
        "speed": 0,
        "eta": 0,
        "start": time(),
        "last_update": time(),
        "last_status": "starting",
    }
    cancel_markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=f"yt_cancel|{job_id}")]])

    def _edit_caption(text: str, markup=cancel_markup):
        """Edit caption via client (lebih andal daripada via callback query)."""
        return self.edit_message_caption(
            cq.message.chat.id,
            cq.message.id,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )

    try:
        await _edit_caption(f"Preparing <b>{escape(label)}</b>...")
    except MessageNotModified:
        pass
    except MessageIdInvalid:
        # Pesan sudah dihapus user — lanjutkan download tanpa progress UI
        pass

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "%(title).180B %(height)sp%(fps)sfps %(format_id)s.%(ext)s")

    def progress_hook(status):
        state = ACTIVE_DOWNLOADS.get(job_id)
        if not state:
            return
        if state["cancelled"]:
            raise DownloadCancelled("Cancelled by user")
        state["last_update"] = time()
        if status.get("status") == "downloading":
            downloaded = status.get("downloaded_bytes") or 0
            total = status.get("total_bytes") or status.get("total_bytes_estimate") or 0
            # Format gabungan (video+audio) memanggil hook 2x — progress
            # stream kedua mulai dari 0. Clamp dengan max supaya bar
            # tidak pernah mundur.
            state["downloaded"] = max(state["downloaded"], downloaded)
            state["total"] = max(state["total"], total)
            if state["total"] and state["downloaded"] > state["total"]:
                state["downloaded"] = state["total"]
            state["speed"] = status.get("speed") or 0
            state["eta"] = status.get("eta") or 0
            state["last_status"] = "downloading"
        elif status.get("status") == "finished":
            state["last_status"] = "finished"

    def do_download():
        # Video: selector sudah memilih format H.264/AVC + audio AAC (m4a)
        # di parse_quality_tree, lalu di-merge ke container MP4.
        # Audio: ambil AAC (m4a) lalu ekstrak/konversi ke AAC murni.
        ydl_opts = build_ydl_opts({
            "outtmpl": file_path,
            "noprogress": True,
            "format": option["format"],
            "progress_hooks": [progress_hook],
            "merge_output_format": "mp4",
        })
        if option["kind"] == "audio":
            ydl_opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": option.get("codec", "aac"), "preferredquality": option.get("bitrate", "192")},
                {"key": "FFmpegMetadata", "add_metadata": True},
                {"key": "EmbedThumbnail"},
            ]
        else:
            ydl_opts["postprocessors"] = [
                {"key": "FFmpegMetadata", "add_metadata": True},
            ]
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data["url"], download=True)
            requested = info.get("requested_downloads") or []
            if requested and requested[0].get("filepath"):
                return requested[0]["filepath"]
            return ydl.prepare_filename(info)

    download_task = asyncio.create_task(asyncio.to_thread(do_download))
    status_text = ""
    title = data.get("title") or "Untitled"

    while not download_task.done():
        state = ACTIVE_DOWNLOADS[job_id]
        # Hook diam >8 detik tapi download masih jalan => yt-dlp sedang
        # merge/post-process (hook tidak dipanggil pada fase ini).
        if time() - state["last_update"] > 8 and state["downloaded"] > 0:
            text = dl_finalizing_text(label, mention)
        else:
            text = dl_progress_text(state, label, title, mention)
        if text != status_text:
            try:
                await _edit_caption(text)
                status_text = text
            except (MessageNotModified, QueryIdInvalid):
                pass
            except MessageIdInvalid:
                # Pesan dihapus user — stop update UI, biarkan download jalan
                status_text = text
                break
        await asyncio.sleep(3)

    try:
        downloaded_file = await download_task
    except DownloadCancelled:
        ACTIVE_DOWNLOADS.pop(job_id, None)
        with contextlib.suppress(MessageIdInvalid):
            return await _edit_caption("❌ Download cancelled.")
        return
    except DownloadError as err:
        ACTIVE_DOWNLOADS.pop(job_id, None)
        with contextlib.suppress(MessageIdInvalid):
            return await _edit_caption(
                f"❌ Download failed: <code>{format_ytdl_error(err)}</code>"
            )
        return
    except Exception as err:
        ACTIVE_DOWNLOADS.pop(job_id, None)
        with contextlib.suppress(MessageIdInvalid):
            return await _edit_caption(
                f"❌ Download error: <code>{format_ytdl_error(err)}</code>"
            )
        return

    if "%" in downloaded_file or not os.path.exists(downloaded_file):
        downloaded_file = resolve_downloaded_file(output_dir, "", option.get("ext"))
    if not downloaded_file or not os.path.exists(downloaded_file):
        ACTIVE_DOWNLOADS.pop(job_id, None)
        with contextlib.suppress(MessageIdInvalid):
            return await _edit_caption("❌ Downloaded file not found.")
        return

    thumb_file = await download_thumb_file(data.get("thumb"), job_id, output_dir)
    if not thumb_file and option["kind"] == "video":
        thumb_file = await generate_thumb_with_ffmpeg(downloaded_file, job_id, output_dir)

    try:
        await _edit_caption("<emoji id=5319190934510904031>⏳</emoji> Uploading...")
    except (MessageNotModified, QueryIdInvalid, MessageIdInvalid):
        pass

    try:
        if option["kind"] == "audio":
            performer = data.get("artist") or data.get("uploader") or None
            title = data.get("track") or data.get("title")
            meta = []
            if performer:
                meta.append(f"🎤 {performer}")
            if data.get("album"):
                meta.append(f"💿 {data.get('album')}")
            if data.get("release_date"):
                meta.append(f"📅 {data.get('release_date')}")
            if data.get("duration"):
                meta.append(f"⏱ {time_formatter(data['duration']).strip()}")
            caption = dl_caption_meta(title or "Audio", meta, mention)
            media = InputMediaAudio(
                media=downloaded_file,
                caption=caption,
                parse_mode=ParseMode.HTML,
                duration=data.get("duration") or None,
                performer=performer,
                title=title,
                thumb=thumb_file,
            )
        else:
            meta = []
            if data.get("uploader"):
                meta.append(f"👤 {data.get('uploader')}")
            if data.get("duration"):
                meta.append(f"⏱ {time_formatter(data['duration']).strip()}")
            caption = dl_caption_meta(title, meta, mention)
            media = InputMediaVideo(
                media=downloaded_file,
                caption=caption,
                parse_mode=ParseMode.HTML,
                duration=data.get("duration") or None,
                thumb=thumb_file,
                supports_streaming=True,
            )
        await self.edit_message_media(
            cq.message.chat.id,
            cq.message.id,
            media=media,
            reply_markup=None,
        )
    except DownloadCancelled:
        with contextlib.suppress(MessageIdInvalid):
            await _edit_caption("❌ Upload cancelled.")
    except Exception as err:
        with contextlib.suppress(MessageIdInvalid):
            await _edit_caption(f"❌ Upload failed: <code>{err}</code>")
    finally:
        ACTIVE_DOWNLOADS.pop(job_id, None)
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)


@app.on_callback_query(filters.regex(r"^yt_cancel\|"))
@use_chat_lang()
async def ytdl_cancel_callback(_, cq: CallbackQuery, strings):
    job_id = cq.data.split("|")[1]
    task = ACTIVE_DOWNLOADS.get(job_id)
    if not task:
        return await cq.answer("Task already finished", show_alert=True)
    task["cancelled"] = True
    try:
        await cq.answer("Cancelling task...")
    except QueryIdInvalid:
        pass


@app.on_callback_query(filters.regex(r"^ytdl_scroll"))
@use_chat_lang()
async def ytdl_scroll_callback(_, cq: CallbackQuery, strings):
    callback = cq.data.split("|")
    search_key = callback[1]
    page = int(callback[2])
    data = YT_DB.get(search_key)
    if not data:
        return await cq.answer("Search expired", show_alert=True)
    if cq.from_user.id != data["user_id"]:
        return await cq.answer(strings("unauth"), True)

    results = data["results"]
    if page < 0 or page > len(results) - 1:
        return await cq.answer(strings("endlist"), show_alert=True)
    i = results[page]
    out = strings("yts_msg").format(
        pub=i.get("upload_date") or "-",
        dur=time_formatter(i.get("duration") or 0),
        vi=humanbytes(i.get("view_count") or 0),
        clink=i.get("channel_url") or i.get("uploader_url") or "https://youtube.com",
        cname=i.get("channel") or i.get("uploader") or "Unknown",
    )

    scroll_btn = [[]]
    if page > 0:
        scroll_btn[0].append(InlineKeyboardButton(strings("back"), callback_data=f"ytdl_scroll|{search_key}|{page - 1}"))
    scroll_btn[0].append(InlineKeyboardButton(f"{page + 1}/{len(results)}", callback_data=f"ytdl_scroll|{search_key}|{page}"))
    if page < len(results) - 1:
        scroll_btn[0].append(InlineKeyboardButton("Next", callback_data=f"ytdl_scroll|{search_key}|{page + 1}"))

    btn = InlineKeyboardMarkup(scroll_btn + [[InlineKeyboardButton(strings("dl_btn"), callback_data=f"yt_gen|{search_key}|{page}")]])
    await cq.edit_message_media(InputMediaPhoto(await get_ytthumb(i.get("id")), caption=out), reply_markup=btn)


@app.on_callback_query(filters.regex(r"^yt_gen\|"))
@use_chat_lang()
async def ytdl_gen_from_search(_, cq: CallbackQuery, strings):
    callback = cq.data.split("|")
    search_key = callback[1]
    page = int(callback[2])
    data = YT_DB.get(search_key)
    if not data:
        return await cq.answer("Search expired", show_alert=True)
    if cq.from_user.id != data["user_id"]:
        return await cq.answer(strings("unauth"), True)

    entry = data["results"][page]
    url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry.get('id')}"

    stop_event = asyncio.Event()
    anim_task = asyncio.create_task(animate_processing(cq.message, PROCESS_TEXT, stop_event))
    try:
        info = await yt_extract(url)
    except DownloadError as err:
        return await cq.edit_message_caption(
            f"❌ <code>{format_ytdl_error(err)}</code>", parse_mode=ParseMode.HTML
        )
    except asyncio.TimeoutError:
        return await cq.edit_message_caption(
            "❌ Request timed out while contacting yt-dlp source.",
            parse_mode=ParseMode.HTML,
        )
    except Exception as err:
        return await cq.edit_message_caption(
            f"{strings('err_parse')}\n\n<code>{format_ytdl_error(err)}</code>",
            parse_mode=ParseMode.HTML,
        )
    finally:
        stop_event.set()
        await anim_task

    cache_key = rand_key()
    tree = parse_quality_tree(info)
    YTDL_CACHE[cache_key] = {
        "url": url,
        "title": info.get("title") or entry.get("title") or "Untitled",
        "thumb": info.get("thumbnail") or "assets/thumb.jpg",
        "duration": int(info.get("duration") or entry.get("duration") or 0),
        "uploader": info.get("uploader") or info.get("channel") or "",
        "artist": info.get("artist") or info.get("creator") or "",
        "album": info.get("album") or "",
        "track": info.get("track") or info.get("title") or entry.get("title") or "",
        "release_date": info.get("release_date") or info.get("upload_date") or "",
        "quality_tree": tree,
        "user_id": cq.from_user.id,
    }
    await cq.edit_message_reply_markup(reply_markup=quality_markup(cache_key, tree))


async def get_ytthumb(videoid: str | None):
    if not videoid:
        return "https://i.imgur.com/4LwPLai.png"
    thumb_quality = ["maxresdefault.jpg", "hqdefault.jpg", "sddefault.jpg", "mqdefault.jpg", "default.jpg"]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for quality in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{quality}"
        if (await fetch.get(link)).status_code == 200:
            thumb_link = link
            break
    return thumb_link
