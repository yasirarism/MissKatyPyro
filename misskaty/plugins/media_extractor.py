"""
* @author        yasir <yasiramunandar@gmail.com>
* @created       2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

import asyncio
import contextlib
import json
import os
import traceback
from logging import getLogger
from re import I
from re import split as ngesplit
from time import time
from urllib.parse import unquote

from pyrogram import Client, filters
from pyrogram import types as pyro_types
from pyrogram.file_id import FileId
from pyrogram.errors import FloodWait, MessageIdInvalid, MessageNotModified, QueryIdInvalid
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.human_read import get_readable_time
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.pyro_progress import humanbytes, progress_for_pyrogram, time_formatter
from misskaty.helper.tools import get_random_string
from misskaty.plugins.dev import shell_exec
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger("MissKaty")

ARCH_EXT = (
    "mkv",
    "mp4",
    "mov",
    "wmv",
    "3gp",
    "mpg",
    "webm",
    "avi",
    "flv",
    "m4v",
)

__MODULE__ = "MediaExtract"
__HELP__ = """
/extractmedia [URL] - Extract subtitle or audio from video using link. (Not support TG File to reduce bandwith usage.)
/converttosrt [Reply to .ass or .vtt TG File] - Convert from .ass or .vtt to srt
/converttoass [Reply to .srt or .vtt TG File] - Convert from .srt or .vtt to srt
"""

# Cache sementara: message_id -> {link, user_id, created_at}. Dipakai supaya
# callback tidak bergantung pada `reply_to_message` yang bisa hilang/None.
# Key = message_id pesan yang berisi tombol, expired 60 detik.
_EXTRACT_SESSIONS: dict[int, dict] = {}
_EXTRACT_TTL = 60  # detik setelah daftar stream ditampilkan
_ACTIVE_EXTRACTS: dict[int, dict] = {}


def _purge_expired_sessions():
    """Hapus session yang sudah lewat TTL supaya dict tidak membengkak."""
    now = time()
    expired = [
        mid
        for mid, s in _EXTRACT_SESSIONS.items()
        if now - s.get("created_at", 0) > _EXTRACT_TTL
    ]
    for mid in expired:
        _EXTRACT_SESSIONS.pop(mid, None)


def get_base_name(orig_path: str):
    if ext := [ext for ext in ARCH_EXT if orig_path.lower().endswith(ext)]:
        ext = ext[0]
        return ngesplit(f"{ext}$", orig_path, maxsplit=1, flags=I)[0]


def get_subname(lang, url, ext):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1 or not get_base_name(
        os.path.basename(unquote(scheme_removed))
    ):
        return f"[{lang.upper()}] MissKatySub{get_random_string(4)}.{ext}"
    return f"[{lang.upper()}] {get_base_name(os.path.basename(unquote(scheme_removed)))}{get_random_string(3)}.{ext}"


async def _expire_extract_session(message_id: int):
    """Expire menu, remove downloaded Telegram source, and update its message."""
    try:
        await asyncio.sleep(_EXTRACT_TTL)
        session = _EXTRACT_SESSIONS.pop(message_id, None)
        if not session:
            return
        if session.get("local_file"):
            with contextlib.suppress(FileNotFoundError):
                os.remove(session.get("link", ""))
        with contextlib.suppress(Exception):
            await app.edit_message_text(
                session["chat_id"],
                message_id,
                "⌛ <b>Task expired.</b>\nSilakan jalankan /extractmedia lagi.",
            )
    except asyncio.CancelledError:
        raise
    except Exception:
        LOGGER.error(traceback.format_exc())


async def _probe_media(source: str) -> dict:
    """Probe local file/URL without shell interpolation."""
    proc = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", source,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if proc.returncode:
        raise RuntimeError(err.decode("utf-8", "replace").strip() or "ffprobe failed")
    return json.loads(out.decode("utf-8", "replace"))


def _media_source(reply: Message):
    media = reply.video or reply.document or reply.audio
    if not media:
        return None
    mime = getattr(media, "mime_type", "") or ""
    filename = getattr(media, "file_name", "") or ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if reply.video or reply.audio or mime.startswith(("video/", "audio/")) or extension in ARCH_EXT:
        return media
    return None


class StreamExtractHelper:
    """Helper kecil untuk validasi dan parsing callback stream extract."""

    @staticmethod
    def sanitize(value: str) -> str:
        return str(value).replace("#", "_")

    @staticmethod
    def build_callback(user_id: int, lang: str, mapping: int | str, codec: str) -> str:
        return (
            f"streamextract#{user_id}#{StreamExtractHelper.sanitize(lang)}"
            f"#0:{mapping}#{StreamExtractHelper.sanitize(codec)}"
        )

    @staticmethod
    def parse_callback(data: str) -> tuple[int, str, str, str] | None:
        """Parse payload -> (user_id, lang, map_code, codec). None kalau invalid."""
        try:
            _, uid, lang, map_code, codec = data.split("#", 4)
            return int(uid), lang, map_code, codec
        except (ValueError, TypeError):
            return None

    @staticmethod
    def is_authorized(user_id: int, owner_id: int) -> bool:
        return user_id == owner_id

    @staticmethod
    def get_source_link(message_id: int) -> str | None:
        _purge_expired_sessions()
        session = _EXTRACT_SESSIONS.get(message_id)
        if not session:
            return None
        return session.get("link")


def _cancel_markup(message_id: int, user_id: int, label: str = "❌ Cancel"):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=f"extractcancel#{message_id}#{user_id}")]]
    )


@app.on_callback_query(filters.regex(r"^extractcancel#"))
async def cancel_extract(_, query: CallbackQuery):
    try:
        _, message_id, user_id = (query.data or "").split("#", 2)
        if query.from_user.id != int(user_id):
            return await query.answer("Not yours!", True)
        job = _ACTIVE_EXTRACTS.get(int(message_id))
        if not job:
            return await query.answer("Task sudah selesai.", True)
        task = job.get("task")
        if task and not task.done():
            task.cancel()
        else:
            job["cancelled"] = True
        await query.answer("Membatalkan download...", True)
    except (ValueError, TypeError, QueryIdInvalid):
        with contextlib.suppress(Exception):
            await query.answer("Task tidak valid.", True)


async def _extract_progress(current, total, label, message, start, dc_id, job_id, user_id):
    job = _ACTIVE_EXTRACTS.get(int(job_id), {})
    if job.get("cancelled"):
        raise asyncio.CancelledError
    await progress_for_pyrogram(
        current, total, label, message, start, dc_id,
        reply_markup=_cancel_markup(job_id, user_id),
    )


@app.on_message(filters.command(["ceksub", "extractmedia"], COMMAND_HANDLER))
@use_chat_lang()
async def ceksub(_, ctx: Message, strings):
    reply = ctx.reply_to_message
    media = _media_source(reply) if reply else None
    if len(ctx.command) == 1 and not media:
        return await ctx.reply(
            strings("sub_extr_help").format(cmd=ctx.command[0]), del_in=5
        )

    source = ctx.command[1] if len(ctx.command) > 1 else None
    source_path = None
    owner_id = ctx.from_user.id if ctx.from_user else 0
    start_time = time()
    pesan = await ctx.reply(strings("progress_str"))
    _ACTIVE_EXTRACTS[pesan.id] = {"cancelled": False, "user_id": owner_id}
    if media:
        os.makedirs("downloads", exist_ok=True)
        dc_id = FileId.decode(media.file_id).dc_id
        await pesan.edit(
            strings("progress_str") + f"\nDownloading Telegram file...\nDC ID: {dc_id}",
            reply_markup=_cancel_markup(pesan.id, owner_id),
        )
        dl_name = f"downloads/{pesan.id}_{os.path.basename(getattr(media, 'file_name', '') or f'media_{pesan.id}')}"
        task = asyncio.create_task(
            reply.download(
                file_name=dl_name,
                progress=_extract_progress,
                progress_args=("Downloading Telegram file...", pesan, time(), dc_id, pesan.id, owner_id),
            )
        )
        _ACTIVE_EXTRACTS[pesan.id] = {"task": task, "user_id": owner_id, "cancelled": False}
        try:
            source_path = await task
        except asyncio.CancelledError:
            _ACTIVE_EXTRACTS.pop(pesan.id, None)
            with contextlib.suppress(FileNotFoundError):
                os.remove(dl_name)
            with contextlib.suppress(Exception):
                await pesan.edit("❌ Download dibatalkan.")
            return
        if not source_path:
            _ACTIVE_EXTRACTS.pop(pesan.id, None)
            return await pesan.edit(strings("fail_extr_media"))
        source = source_path
    if not source:
        await pesan.delete()
        return await ctx.reply(
            strings("sub_extr_help").format(cmd=ctx.command[0]), del_in=5
        )

    try:
        details = await _probe_media(source)
        streams = details.get("streams", [])
        if not any(s.get("codec_type") in ("audio", "subtitle") for s in streams):
            if source_path:
                with contextlib.suppress(FileNotFoundError):
                    os.remove(source_path)
            return await pesan.edit(strings("fail_extr_media"))

        _EXTRACT_SESSIONS[pesan.id] = {
            "link": source,
            "user_id": owner_id,
            "created_at": time(),
            "local_file": bool(source_path),
            "chat_id": pesan.chat.id,
        }
        _EXTRACT_SESSIONS[pesan.id]["expiry_task"] = asyncio.create_task(
            _expire_extract_session(pesan.id)
        )
        buttons = []
        for stream in streams:
            mapping = stream.get("index")
            stream_name = stream.get("codec_name", "-")
            stream_type = stream.get("codec_type")
            if stream_type not in ("audio", "subtitle"):
                continue
            lang = (stream.get("tags") or {}).get("language", mapping)
            buttons.append([
                InlineKeyboardButton(
                    f"0:{mapping}({lang}): {stream_type}: {stream_name}",
                    callback_data=StreamExtractHelper.build_callback(owner_id, lang, mapping, stream_name),
                )
            ])
        timelog = time() - start_time
        buttons.append([InlineKeyboardButton(strings("cancel_btn"), callback_data=f"close#{owner_id}")])
        await pesan.edit(
            strings("press_btn_msg").format(timelog=get_readable_time(timelog)),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        _ACTIVE_EXTRACTS.pop(pesan.id, None)
    except Exception:
        LOGGER.error(traceback.format_exc())
        if source_path:
            with contextlib.suppress(FileNotFoundError):
                os.remove(source_path)
        _EXTRACT_SESSIONS.pop(pesan.id, None)
        _ACTIVE_EXTRACTS.pop(pesan.id, None)
        await pesan.edit(strings("fail_extr_media"))


@app.on_message(filters.command(["converttosrt", "converttoass"], COMMAND_HANDLER))
@capture_err
@use_chat_lang()
async def convertsrt(self: Client, ctx: Message, strings):
    reply = ctx.reply_to_message
    if (
        not reply
        or not reply.document
        or not reply.document.file_name
        or not reply.document.file_name.endswith((".vtt", ".ass", ".srt"))
    ):
        return await ctx.reply(
            strings("conv_sub_help").format(cmd=ctx.command[0]), del_in=6
        )
    msg = await ctx.reply(strings("convert_str"))
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    dl = await reply.download(file_name="downloads/")
    filename = dl.split("/", 3)[3]
    LOGGER.info(
        f"ConvertSub: {filename} by {ctx.from_user.first_name if ctx.from_user else ctx.sender_chat.title} [{ctx.from_user.id if ctx.from_user else ctx.sender_chat.id}]"
    )
    suffix = "srt" if ctx.command[0] == "converttosrt" else "ass"
    await shell_exec(f"ffmpeg -i '{dl}' 'downloads/{filename}.{suffix}'")
    c_time = time()
    await ctx.reply_document(
        f"downloads/{filename}.{suffix}",
        caption=strings("capt_conv_sub").format(nf=filename, bot=self.me.username),
        thumb="assets/thumb.jpg",
        progress=progress_for_pyrogram,
        progress_args=(strings("up_str"), msg, c_time, self.me.dc_id),
    )
    await msg.delete_msg()
    try:
        os.remove(dl)
        os.remove(f"downloads/{filename}.{suffix}")
    except Exception:
        pass


@app.on_callback_query(filters.regex(r"^streamextract#"))
@use_chat_lang()
async def stream_extract(self: Client, update: CallbackQuery, strings):
    cb_data = update.data or ""
    parsed = StreamExtractHelper.parse_callback(cb_data)
    if not parsed:
        return await update.answer(strings("invalid_cb"), True)
    owner_id, lang, map_code, codec = parsed

    # Hanya pemilik link yang boleh mengekstrak
    if not StreamExtractHelper.is_authorized(update.from_user.id, owner_id):
        return await update.answer(strings("unauth_cb"), True)

    link = StreamExtractHelper.get_source_link(update.message.id)
    session = _EXTRACT_SESSIONS.get(update.message.id)
    if not link or not session:
        return await update.answer("⌛ Task expired.", True)
    expiry_task = session.pop("expiry_task", None)
    if expiry_task and not expiry_task.done():
        expiry_task.cancel()
    await update.message.edit(strings("progress_str"))
    if codec in ("aac", "m4a"):
        ext = "aac"
    elif codec == "mp3":
        ext = "mp3"
    elif codec == "eac3":
        ext = "eac3"
    elif codec in ("ass", "ssa"):
        ext = "ass"
    elif codec in ("webvtt", "vtt"):
        ext = "vtt"
    else:
        ext = "srt"
    start_time = time()
    namafile = get_subname(lang, link, ext)
    if session.get("local_file"):
        base = os.path.splitext(os.path.basename(link))[0]
        namafile = f"[{str(lang).upper()}] {base}.{ext}"
    try:
        LOGGER.info(
            f"ExtractSub: {namafile} by {update.from_user.first_name} [{update.from_user.id}]"
        )
        ffmpeg_args = ["ffmpeg", "-y", "-i", link, "-map", map_code]
        if codec in ("ass", "ssa", "subrip", "webvtt", "mov_text"):
            ffmpeg_args += ["-c:s", "copy"]
        elif codec in ("aac", "mp3", "eac3", "opus", "ac3"):
            ffmpeg_args += ["-vn", "-c:a", "copy"]
        ffmpeg_args.append(namafile)
        proc = await asyncio.create_subprocess_exec(
            *ffmpeg_args,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, fferr = await proc.communicate()
        if proc.returncode:
            raise RuntimeError(fferr.decode("utf-8", "replace").strip() or "ffmpeg failed")
        timelog = time() - start_time
        c_time = time()
        await update.message.reply_document(
            namafile,
            caption=strings("capt_extr_sub").format(
                nf=namafile, bot=self.me.username, timelog=get_readable_time(timelog)
            ),
            reply_parameters=pyro_types.ReplyParameters(message_id=update.message.id),
            thumb="assets/thumb.jpg",
            progress=progress_for_pyrogram,
            progress_args=(strings("up_str"), update.message, c_time, self.me.dc_id),
        )
        await update.message.delete_msg()
        try:
            os.remove(namafile)
        except Exception:
            pass
        if session.get("local_file"):
            with contextlib.suppress(FileNotFoundError):
                os.remove(link)
        _EXTRACT_SESSIONS.pop(update.message.id, None)
    except Exception as e:
        try:
            os.remove(namafile)
        except Exception:
            pass
        if session.get("local_file"):
            with contextlib.suppress(FileNotFoundError):
                os.remove(link)
        _EXTRACT_SESSIONS.pop(update.message.id, None)
        await update.message.edit(strings("fail_extr_sub").format(link=link, e=e))
