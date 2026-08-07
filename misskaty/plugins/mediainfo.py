"""
* @author        yasir <yasiramunandar@gmail.com>
* @date          2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

import io
import os
import subprocess
import time
from logging import getLogger
from os import path
from os import remove as osremove

from pyrogram import Client, filters
from pyrogram.file_id import FileId, FileType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import app
from misskaty.helper import post_to_telegraph, progress_for_pyrogram, runcmd
from misskaty.helper.chat_utils import get_file_id
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.mediainfo_paste import mediainfo_paste
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger("MissKaty")

# ---------------------------------------------------------------------------
# Partial download settings (head + tail) — cukup ambil sebagian kecil file
# untuk dianalisa MediaInfo, tanpa harus mengunduh file utuh.
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1024 * 1024  # 1 MiB per chunk (batas upload.getFile)
HEAD_CHUNKS = 8  # 8 MiB awal
TAIL_CHUNKS = 8  # 8 MiB akhir
FULL_DL_LIMIT = 2_097_152_000  # 2 GiB — batas aman fallback download penuh
PARTIAL_LIMIT = 4_294_967_296  # 4 GiB — partial analysis tetap bisa


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


def _looks_complete(out: str | None) -> bool:
    """Heuristik: output mediainfo dianggap lengkap jika ada section utama."""
    if not out:
        return False
    return any(section in out for section in ("General", "Video", "Audio"))


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
@use_chat_lang()
async def mediainfo(client: Client, ctx: Message, strings):
    if ctx.reply_to_message and ctx.reply_to_message.media:
        process = await ctx.reply(strings("processing_text"))
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
                    progress=progress_for_pyrogram,
                    progress_args=(strings("dl_args_text"), process, c_time, dc_id),
                )
            except FileNotFoundError:
                return await process.edit("ERROR: FileNotFound.")
            file_path = path.join("downloads/", path.basename(dl))

        output_ = await runcmd(f'mediainfo "{file_path}"')
        out = output_[0] if len(output_) != 0 else None

        # --- Hasil partial kurang lengkap -> fallback download penuh ---
        if partial_used and not _looks_complete(out):
            LOGGER.info("Partial analysis kurang lengkap, fallback full download")
            osremove(file_path)
            if file_size > FULL_DL_LIMIT:
                return await process.edit(strings("dl_limit_exceeded"), del_in=6)
            try:
                dl = await ctx.reply_to_message.download(
                    file_name="downloads/",
                    progress=progress_for_pyrogram,
                    progress_args=(strings("dl_args_text"), process, c_time, dc_id),
                )
            except FileNotFoundError:
                return await process.edit("ERROR: FileNotFound.")
            file_path = path.join("downloads/", path.basename(dl))
            output_ = await runcmd(f'mediainfo "{file_path}"')
            out = output_[0] if len(output_) != 0 else None

        body_text = f"""
MissKatyBot MediaInfo
JSON
<pre>{getattr(file_info, 'message_type', 'Unknown')}</pre>
    
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
        try:
            osremove(file_path)
        except Exception:
            pass
    else:
        try:
            link = ctx.input
            process = await ctx.reply(strings("wait_msg"))
            try:
                # `mediainfo` CLI membaca URL remote secara parsial (HTTP range)
                # — tidak perlu download penuh juga.
                output = subprocess.check_output(["mediainfo", f"{link}"]).decode(
                    "utf-8"
                )
            except Exception:
                return await process.edit(strings("err_link"))
            body_text = f"""
            MissKatyBot MediaInfo
            <pre>{output}</pre>
            """
            # link = await post_to_telegraph(False, title, body_text)
            try:
                link = await mediainfo_paste(output, "MissKaty Mediainfo")
                markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=strings("viweb"), url=link)]]
                )
            except Exception:
                try:
                    link = await post_to_telegraph(
                        False, "MissKaty MediaInfo", body_text
                    )
                    markup = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text=strings("viweb"), url=link)]]
                    )
                except Exception:
                    markup = None
            with io.BytesIO(str.encode(output)) as out_file:
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
        except IndexError:
            return await ctx.reply(
                strings("mediainfo_help").format(cmd=ctx.command[0]), del_in=6
            )
