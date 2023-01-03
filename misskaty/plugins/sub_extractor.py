"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from misskaty import app, BOT_USERNAME
from logging import getLogger
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.plugins.dev import shell_exec
import json, os, traceback
from time import perf_counter
from re import split as ngesplit, I
from urllib.parse import unquote
from misskaty.helper.tools import get_random_string

LOGGER = getLogger(__name__)

ARCH_EXT = [".mkv", ".avi", ".mp4", ".mov"]

__MODULE__ = "MediaExtract"
__HELP__ = """
/extractmedia [URL] - Extract subtitle or audio from video using link. (Not support TG File to reduce bandwith usage.)
/converttosrt [Reply to .ass or .vtt TG File] - Convert from .ass or .vtt to srt
"""


def get_base_name(orig_path: str):
    if ext := [ext for ext in ARCH_EXT if orig_path.lower().endswith(ext)]:
        ext = ext[0]
        return ngesplit(f"{ext}$", orig_path, maxsplit=1, flags=I)[0]


def get_subname(url, format):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return f"MissKatySub_{get_random_string(4)}.{format}"
    return f"{get_base_name(os.path.basename(unquote(scheme_removed)))}.{format}"


@app.on_message(filters.command(["ceksub", "extractmedia"], COMMAND_HANDLER))
async def ceksub(_, m):
    cmd = m.text.split(" ", 1)
    if len(cmd) == 1:
        return await m.reply(
            f"Gunakan command /{m.command[0]} [link] untuk mengecek subtitle dan audio didalam video."
        )
    link = cmd[1]
    start_time = perf_counter()
    pesan = await m.reply("Sedang memproses perintah..", quote=True)
    try:
        res = (
            await shell_exec(
                f"ffprobe -loglevel 0 -print_format json -show_format -show_streams {link}"
            )
        )[0]
        details = json.loads(res)
        buttons = []
        for stream in details["streams"]:
            mapping = stream["index"]
            try:
                stream_name = stream["codec_name"]
            except:
                stream_name = "-"
            stream_type = stream["codec_type"]
            if stream_type not in ("audio", "subtitle"):
                continue
            try:
                lang = stream["tags"]["language"]
            except:
                lang = mapping
            buttons.append(
                [
                    InlineKeyboardButton(
                        f"0:{mapping}({lang}): {stream_type}: {stream_name}",
                        f"streamextract_{mapping}_{stream_name}",
                    )
                ]
            )
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        buttons.append([InlineKeyboardButton("Cancel", "cancel")])
        await pesan.edit(
            f"Press the button below to extract subtitles/audio. Only support direct link at this time.\nProcessed in {timelog}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception:
        err = traceback.format_exc()
        await pesan.edit(
            f"Failed extract media, make sure your link is not protected by WAF or maybe inaccessible for bot."
        )


@app.on_message(filters.command(["converttosrt"], COMMAND_HANDLER))
@capture_err
async def convertsrt(c, m):
    reply = m.reply_to_message
    if (
        not reply
        and reply.document
        and (
            reply.document.file_name.endswith(".vtt")
            or reply.document.file_name.endswith(".ass")
        )
    ):
        return await m.reply(
            f"Use command /{m.command[0]} by reply to .ass or .vtt file, to convert subtitle from .ass or .vtt to srt."
        )
    msg = await m.reply("⏳ Converting...")
    dl = await reply.download()
    filename = dl.split("/", 3)[3]
    LOGGER.info(
        f"ConvertSub: {filename} by {m.from_user.first_name} [{m.from_user.id}]"
    )
    (await shell_exec(f"mediaextract -i '{dl}' '{filename}'.srt"))[0]
    await m.reply_document(
        f"{filename}.srt", caption=f"{filename}.srt\n\nConverted by @{c.me.username}"
    )
    await msg.delete()
    try:
        os.remove(dl)
        os.remove(f"{filename}.srt")
    except:
        pass


@app.on_callback_query(filters.regex(r"^streamextract_"))
async def stream_extract(bot, update):
    cb_data = update.data
    usr = update.message.reply_to_message
    if update.from_user.id != usr.from_user.id:
        return await update.answer("⚠️ Access Denied!", True)
    _, map, codec = cb_data.split("_")
    try:
        link = update.message.reply_to_message.command[1]
    except:
        return await update.answer("⚠️ DONT DELETE YOUR MESSAGE!", True)
    await update.message.edit("⏳ Processing...")
    try:
        if codec == "aac":
            format = "aac"
        elif codec == "mp3":
            format = "mp3"
        elif codec == "eac3":
            format = "eac3"
        elif codec == "subrip":
            format = "srt"
        elif codec == "ass":
            format == "ass"
        else:
            format = None
        if not format:
            return await update.answer(
                "⚠️ Unsupported format, try extract manual using ffmpeg"
            )
        start_time = perf_counter()
        namafile = get_subname(link, format)
        LOGGER.info(
            f"ExtractSub: {namafile} by {update.from_user.first_name} [{update.from_user.id}]"
        )
        extract = (await shell_exec(f"mediaextract -i {link} -map 0:{map} {namafile}"))[
            0
        ]
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        await update.message.reply_document(
            namafile,
            caption=f"<b>Filename:</b> <code>{namafile}</code>\n\nExtracted by @{bot.me.username} in {timelog}",
            reply_to_message_id=usr.id,
        )
        await update.message.delete()
        try:
            os.remove(namafile)
        except:
            pass
    except Exception as e:
        await update.message.edit(f"Failed extract sub. \n\nERROR: {e}")
