"""
* @author        yasir <yasiramunandar@gmail.com>
* @date          2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

import asyncio
import contextlib
import io
import math
import os
import time
from logging import getLogger
from os import path
from os import remove as osremove

import httpx
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    MessageIdInvalid,
    MessageNotModified,
    QueryIdInvalid,
)
from pyrogram.file_id import FileId, FileType
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import app
from misskaty.helper import post_to_telegraph, runcmd
from misskaty.helper.chat_utils import get_file_id
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.mediainfo_paste import mediainfo_paste
from misskaty.helper.pyro_progress import humanbytes, time_formatter
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger("MissKaty")

# ---------------------------------------------------------------------------
# Cancel support: ACTIVE_MEDIAINFO[gid] = {"cancelled": bool}
# gid = message.id dari perintah /mediainfo. Tombol Cancel meng-flag pesan;
# progress callback & loop download URL mengecek flag -> raise CancelledError.
# ---------------------------------------------------------------------------
ACTIVE_MEDIAINFO: dict[int, dict] = {}


def _mi_cancel_markup(gid: int, uid: int, label: str = "❌ Cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=f"miocancel#{gid}#{uid}")]]
    )


@app.on_callback_query(filters.regex(r"^miocancel#"))
async def mediainfo_cancel_cb(_, query: CallbackQuery):
    _, gid, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        with contextlib.suppress(QueryIdInvalid):
            return await query.answer("Not yours!", True)
    info = ACTIVE_MEDIAINFO.get(int(gid))
    if not info:
        with contextlib.suppress(QueryIdInvalid):
            return await query.answer("Task sudah selesai / tidak ditemukan.", True)
    info["cancelled"] = True
    with contextlib.suppress(QueryIdInvalid):
        await query.answer("Membatalkan download...", True)


async def _mi_progress(current, total, ud_type, message, start, dc_id, gid, uid):
    """progress_for_pyrogram + tombol Cancel tetap tampil + cek flag cancel."""
    if ACTIVE_MEDIAINFO.get(int(gid), {}).get("cancelled"):
        raise asyncio.CancelledError
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        elapsed_time = round(diff)
        if elapsed_time == 0:
            return
        speed = current / diff
        time_to_completion = round((total - current) / speed)
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = time_formatter(elapsed_time)
        estimated_total_time = time_formatter(estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            "".join(["●" for _ in range(math.floor(percentage / 5))]),
            "".join(["○" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )

        tmp = (
            progress
            + "{0} <b>of</b> {1}\n<b>Speed:</b> {2}/s\n<b>DC ID:</b> {3}\n<b>ETA:</b> {4}</b>\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                dc_id,
                estimated_total_time if estimated_total_time != "" else "0 s",
            )
        )
        # UID requester di-pass eksplisit via progress_args (message adalah
        # pesan proses milik bot, jadi message.from_user = bot, bukan requester).
        markup = _mi_cancel_markup(int(gid), int(uid))
        try:
            await message.edit(f"{ud_type}\n {tmp}", reply_markup=markup)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.edit(f"{ud_type}\n {tmp}", reply_markup=markup)
        except (MessageNotModified, MessageIdInvalid):
            pass

# ---------------------------------------------------------------------------
# Partial download settings (head + tail) — cukup ambil sebagian kecil file
# untuk dianalisa MediaInfo, tanpa harus mengunduh file utuh.
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1024 * 1024  # 1 MiB per chunk (batas upload.getFile)
HEAD_CHUNKS = 8  # 8 MiB awal
TAIL_CHUNKS = 8  # 8 MiB akhir
FULL_DL_LIMIT = 2_097_152_000  # 2 GiB — batas aman fallback download penuh
PARTIAL_LIMIT = 4_294_967_296  # 4 GiB — partial analysis tetap bisa

# URL (HTTP Range) — ukuran per request
URL_CHUNK = 8 * 1024 * 1024  # 8 MiB per Range request
MAX_URL_FULL = 200 * 1024 * 1024  # 200 MiB — cap full download URL tanpa Range


async def _fetch_chunks(client: Client, decoded: FileId, file_size: int, offset_chunks: int, limit_chunks: int) -> bytes:
    """Ambil N chunk (1 MiB) mulai dari offset tertentu via MTProto."""
    data = b""
    async for chunk in client.get_file(
        decoded, file_size=file_size, limit=limit_chunks, offset=offset_chunks
    ):
        data += chunk
    return data


def _is_partial_supported(file_id: FileId) -> bool:
    """Foto tidak bisa via InputDocumentFileLocation — full download saja."""
    return file_id.file_type not in (
        FileType.PHOTO,
        FileType.CHAT_PHOTO,
        FileType.THUMBNAIL,
        FileType.ENCRYPTED,
        FileType.ENCRYPTED_THUMBNAIL,
        FileType.SECURE,
        FileType.SECURE_RAW,
    )


async def _partial_download(client: Client, media, file_size: int) -> str | None:
    """Download head+tail file ke disk, return path temp (None jika gagal).

    - MP4/MOV: `moov` atom umumnya di akhir file -> tail cukup.
    - MKV/WebM/AVI/MP3/FLAC: metadata di awal -> head cukup.
    - Gabungan head+tail membuat MediaInfo bisa membaca hampir semua format
      tanpa mengunduh file utuh.
    """
    try:
        decoded = FileId.decode(media.file_id)
        if not _is_partial_supported(decoded):
            return None

        total_chunks = (file_size // CHUNK_SIZE) + (1 if file_size % CHUNK_SIZE else 0)
        if file_size <= (HEAD_CHUNKS + TAIL_CHUNKS) * CHUNK_SIZE:
            # File kecil: ambil saja semuanya (satu range)
            data = await _fetch_chunks(client, decoded, file_size, 0, total_chunks)
        else:
            head = await _fetch_chunks(client, decoded, file_size, 0, HEAD_CHUNKS)
            tail_start = max(HEAD_CHUNKS, total_chunks - TAIL_CHUNKS)
            tail = await _fetch_chunks(client, decoded, file_size, tail_start, TAIL_CHUNKS)
            data = head + tail

        if not data:
            return None

        os.makedirs("downloads", exist_ok=True)
        temp_path = path.join("downloads", f"mediainfo_{int(time.time())}_{media.file_id[:8] or 'x'}.part")
        with open(temp_path, "wb") as f:
            f.write(data)
        return temp_path
    except Exception as err:
        LOGGER.debug("Partial download gagal, fallback full download: %s", err)
        return None


def _parse_content_range(value: str | None) -> int:
    """Parse header ``Content-Range`` -> total ukuran file (0 jika tidak tahu).

    Contoh: ``bytes 0-8388607/123456789`` -> 123456789
    """
    if not value or "/" not in value:
        return 0
    try:
        return int(value.rsplit("/", 1)[1])
    except (ValueError, IndexError):
        return 0


async def _download_url_partial(url: str, tmp_dir: str, job: str, force_full: bool = False, gid: int = 0):
    """Download URL remote via HTTP Range (head + tail) lalu simpan ke disk.

    - Server support Range (206) -> ambil 8 MiB awal + 8 MiB akhir.
    - Server abaikan Range (200) -> stream sampai 8 MiB saja (head);
      kalau file > MAX_URL_FULL dan tidak support Range -> (None, total)
      supaya pemanggil bisa menolak dengan pesan yang jelas.
    - 403/404 -> (None, 0).
    - ``gid`` diisi saat dipanggil dari /mediainfo: flag cancel dicek tiap
      chunk, kalau user menekan Cancel -> raise ``asyncio.CancelledError``.

    Returns:
        ``(path, total_size)`` — total_size 0 berarti tidak diketahui.
    """
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = path.join(tmp_dir, f"mi_url_{job}.part")

    def _check_cancel():
        if gid and ACTIVE_MEDIAINFO.get(int(gid), {}).get("cancelled"):
            raise asyncio.CancelledError

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            if not force_full:
                async with client.stream(
                    "GET", url, headers={"Range": f"bytes=0-{URL_CHUNK - 1}"}
                ) as resp:
                    if resp.status_code in (403, 404):
                        return None, 0
                    if resp.status_code != 206 and resp.status_code != 200:
                        return None, 0
                    if resp.status_code == 206:
                        total = _parse_content_range(resp.headers.get("content-range"))
                        data = bytearray()
                        async for chunk in resp.aiter_bytes(256 * 1024):
                            _check_cancel()
                            data += chunk
                            if len(data) >= URL_CHUNK:
                                break
                        if total > 2 * URL_CHUNK:
                            async with client.stream(
                                "GET",
                                url,
                                headers={"Range": f"bytes={total - URL_CHUNK}-{total - 1}"},
                            ) as tail_resp:
                                if tail_resp.status_code == 206:
                                    async for chunk in tail_resp.aiter_bytes(256 * 1024):
                                        _check_cancel()
                                        data += chunk
                                        if len(data) >= URL_CHUNK * 2:
                                            break
                        with open(tmp_path, "wb") as f:
                            f.write(data)
                        return tmp_path, total
                    # status 200: server abaikan Range
                    total = _parse_content_range(resp.headers.get("content-range")) or int(
                        resp.headers.get("content-length") or 0
                    )
                    if total > MAX_URL_FULL:
                        return None, total
                    with open(tmp_path, "wb") as f:
                        size = 0
                        async for chunk in resp.aiter_bytes(256 * 1024):
                            _check_cancel()
                            f.write(chunk)
                            size += len(chunk)
                            if size >= URL_CHUNK:
                                break
                    return tmp_path, total
            # force_full: stream seluruh file (dengan cap MAX_URL_FULL)
            async with client.stream("GET", url) as resp:
                if resp.status_code in (403, 404):
                    return None, 0
                if resp.status_code != 200:
                    return None, 0
                with open(tmp_path, "wb") as f:
                    size = 0
                    async for chunk in resp.aiter_bytes(256 * 1024):
                        _check_cancel()
                        f.write(chunk)
                        size += len(chunk)
                        if size >= MAX_URL_FULL:
                            break
                return tmp_path, size
    except asyncio.CancelledError:
        # User menekan Cancel — jangan ditelan except Exception di bawah,
        # biarkan propagate ke handler mediainfo (Python 3.8+: CancelledError
        # turunan BaseException, tapi re-raise eksplisit lebih aman lintas versi).
        raise
    except Exception as err:
        LOGGER.debug("URL partial download gagal: %s", err)
        return None, 0


def _looks_complete(out: str | None) -> bool:
    """Heuristik: output mediainfo dianggap lengkap jika ada section utama."""
    if not out:
        return False
    return any(section in out for section in ("General", "Video", "Audio"))


async def _send_result(ctx: Message, process: Message, out: str, strings, media_type: str = "Unknown"):
    """Buat paste + kirim file hasil mediainfo (dipakai reply & URL path)."""
    body_text = f"""
MissKatyBot MediaInfo
JSON
<pre>{media_type}</pre>
    
DETAILS
<pre>{out or 'Not Supported'}</pre>
    """
    try:
        link = await mediainfo_paste(out, "MissKaty Mediainfo")
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=strings("viweb"), url=link)]]
        )
    except Exception:
        try:
            link = await post_to_telegraph(
                False, "MissKaty MediaInfo", f"<code>{body_text}</code>"
            )
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=strings("viweb"), url=link)]]
            )
        except Exception:
            markup = None
    with io.BytesIO(str.encode(body_text)) as out_file:
        out_file.name = "MissKaty_Mediainfo.txt"
        await ctx.reply_document(
            out_file,
            caption=strings("capt_media").format(
                ment=ctx.from_user.mention
                if ctx.from_user
                else ctx.sender_chat.title
            ),
            thumb="assets/thumb.jpg",
            reply_markup=markup,
        )
        await process.delete()


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
@use_chat_lang()
async def mediainfo(client: Client, ctx: Message, strings):
    gid = ctx.id
    uid = ctx.from_user.id if ctx.from_user else 0
    ACTIVE_MEDIAINFO[gid] = {"cancelled": False}
    file_path: str | None = None
    process: Message | None = None

    async def _cleanup(paths):
        for p in paths:
            with contextlib.suppress(Exception):
                if p and path.exists(p):
                    osremove(p)

    try:
        if ctx.reply_to_message and ctx.reply_to_message.media:
            process = await ctx.reply(
                strings("processing_text"),
                reply_markup=_mi_cancel_markup(gid, uid, strings("cancel_btn")),
            )
            file_info = get_file_id(ctx.reply_to_message)
            if file_info is None:
                return await process.edit(strings("media_invalid"))
            file_size = getattr(file_info, "file_size", 0) or 0
            if file_size > PARTIAL_LIMIT:
                return await process.edit(strings("dl_limit_exceeded"), del_in=6)
            c_time = time.time()
            dc_id = FileId.decode(file_info.file_id).dc_id

            # --- Percobaan 1: partial download (head+tail), tanpa download penuh ---
            file_path = await _partial_download(client, file_info, file_size)
            partial_used = file_path is not None

            if not partial_used:
                if file_size > FULL_DL_LIMIT:
                    return await process.edit(strings("dl_limit_exceeded"), del_in=6)
                try:
                    dl = await ctx.reply_to_message.download(
                        file_name="downloads/",
                        progress=_mi_progress,
                        progress_args=(strings("dl_args_text"), process, c_time, dc_id, gid, uid),
                    )
                except asyncio.CancelledError:
                    raise
                except FileNotFoundError:
                    return await process.edit("ERROR: FileNotFound.")
                file_path = path.join("downloads/", path.basename(dl))

            output_ = await runcmd(f'mediainfo "{file_path}"')
            out = output_[0] if len(output_) != 0 else None

            # --- Hasil partial kurang lengkap -> fallback download penuh ---
            if partial_used and not _looks_complete(out):
                LOGGER.info("Partial analysis kurang lengkap, fallback full download")
                await _cleanup([file_path])
                if file_size > FULL_DL_LIMIT:
                    return await process.edit(strings("dl_limit_exceeded"), del_in=6)
                try:
                    dl = await ctx.reply_to_message.download(
                        file_name="downloads/",
                        progress=_mi_progress,
                        progress_args=(strings("dl_args_text"), process, c_time, dc_id, gid, uid),
                    )
                except asyncio.CancelledError:
                    raise
                except FileNotFoundError:
                    return await process.edit("ERROR: FileNotFound.")
                file_path = path.join("downloads/", path.basename(dl))
                output_ = await runcmd(f'mediainfo "{file_path}"')
                out = output_[0] if len(output_) != 0 else None

            # Output tetap kosong/tidak lengkap -> jangan kirim file kosong
            if not _looks_complete(out):
                await _cleanup([file_path])
                return await process.edit(strings("err_analyze"), del_in=6)

            await _send_result(
                ctx, process, out, strings,
                media_type=getattr(file_info, "message_type", "Unknown"),
            )
            await _cleanup([file_path])
        else:
            link = ctx.input
            # Wajib ada link setelah command — kalau tidak, tampilkan bantuan
            # (jangan trigger analisis kosong).
            if not link:
                return await ctx.reply(
                    strings("mediainfo_help").format(cmd=ctx.command[0]), del_in=6
                )
            process = await ctx.reply(
                strings("wait_msg"), reply_markup=_mi_cancel_markup(gid, uid, strings("cancel_btn"))
            )
            job = f"url{int(time.time())}"

            # Download URL by chunk (HTTP Range) lalu analisis lokal —
            # mengatasi URL yang kena 404 saat dipanggil langsung mediainfo CLI.
            file_path, total = await _download_url_partial(
                link, "downloads", job, gid=gid
            )
            if not file_path:
                return await process.edit(strings("err_link"), del_in=6)

            output_ = await runcmd(f'mediainfo "{file_path}"')
            out = output_[0] if len(output_) != 0 else None

            # Partial kurang lengkap & file masih masuk akal -> coba full stream
            if not _looks_complete(out) and total and total <= MAX_URL_FULL:
                LOGGER.info("URL partial kurang lengkap, coba full download")
                await _cleanup([file_path])
                file_path, _ = await _download_url_partial(
                    link, "downloads", f"{job}_full", force_full=True, gid=gid
                )
                if file_path:
                    output_ = await runcmd(f'mediainfo "{file_path}"')
                    out = output_[0] if len(output_) != 0 else None

            if not _looks_complete(out):
                await _cleanup([file_path])
                return await process.edit(strings("err_analyze"), del_in=6)

            await _send_result(ctx, process, out, strings, media_type="URL")
            await _cleanup([file_path])
    except asyncio.CancelledError:
        LOGGER.info("mediainfo dibatalkan user (gid=%s)", gid)
        await _cleanup([file_path])
        with contextlib.suppress(Exception):
            await process.edit(strings("cancelled_text"), del_in=5)
    finally:
        ACTIVE_MEDIAINFO.pop(gid, None)
