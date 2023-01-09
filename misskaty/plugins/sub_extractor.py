"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from misskaty import app
from logging import getLogger
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.plugins.dev import shell_exec
import json, os, traceback
from time import perf_counter, time
from re import split as ngesplit, I
from urllib.parse import unquote
from misskaty.helper.tools import get_random_string
from misskaty.helper.pyro_progress import progress_for_pyrogram

LOGGER = getLogger(__name__)

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
"""


def get_base_name(orig_path: str):
    if ext := [ext for ext in ARCH_EXT if orig_path.lower().endswith(ext)]:
        ext = ext[0]
        return ngesplit(f"{ext}$", orig_path, maxsplit=1, flags=I)[0]


def get_subname(lang, url, format):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return f"[{lang.upper()}] MissKatySub_{get_random_string(4)}.{format}"
    return f"[{lang.upper()}] {get_base_name(os.path.basename(unquote(scheme_removed)))}.{format}"


@app.on_message(filters.command(["ceksub", "extractmedia"], COMMAND_HANDLER))
async def ceksub(_, m):
    cmd = m.text.split(" ", 1)
    if len(cmd) == 1:
        return await m.reply(f"Gunakan command /{m.command[0]} [link] untuk mengecek subtitle dan audio didalam video.")
    link = cmd[1]
    start_time = perf_counter()
    pesan = await m.reply("Sedang memproses perintah..", quote=True)
    try:
        res = (await shell_exec(f"ffprobe -loglevel 0 -print_format json -show_format -show_streams {link}"))[0]
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
                        f"streamextract#{lang}#0:{mapping}#{stream_name}",
                    )
                ]
            )
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        buttons.append([InlineKeyboardButton("❌ Cancel", f"close#{m.from_user.id}")])
        await pesan.edit(
            f"Press the button below to extract subtitles/audio. Only support direct link at this time.\nProcessed in {timelog}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception:
        traceback.format_exc()
        await pesan.edit(f"Failed extract media, make sure your link is not protected by WAF or maybe inaccessible for bot.")


@app.on_message(filters.command(["converttosrt"], COMMAND_HANDLER))
@capture_err
async def convertsrt(c, m):
    reply = m.reply_to_message
    if not reply and reply.document and (reply.document.file_name.endswith(".vtt") or reply.document.file_name.endswith(".ass")):
        return await m.reply(f"Use command /{m.command[0]} by reply to .ass or .vtt file, to convert subtitle from .ass or .vtt to srt.")
    msg = await m.reply("⏳ Converting...")
    dl = await reply.download()
    filename = dl.split("/", 3)[3]
    LOGGER.info(f"ConvertSub: {filename} by {m.from_user.first_name} [{m.from_user.id}]")
    (await shell_exec(f"mediaextract -i '{dl}' '{filename}.srt'"))[0]
    c_time = time()
    await m.reply_document(
        f"{filename}.srt",
        caption=f"<code>{filename}.srt</code>\n\nConverted by @{c.me.username}",
        progress=progress_for_pyrogram,
        progress_args=("Uploading files..", msg, c_time),
    )
    await msg.delete()
    try:
        os.remove(dl)
        os.remove(f"{filename}.srt")
    except:
        pass


@app.on_callback_query(filters.regex(r"^streamextract#"))
async def stream_extract(bot, update):
    cb_data = update.data
    usr = update.message.reply_to_message
    if update.from_user.id != usr.from_user.id:
        return await update.answer("⚠️ Access Denied!", True)
    _, lang, map, codec = cb_data.split("#")
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
        else:
            format = "srt"
        start_time = perf_counter()
        namafile = get_subname(lang, link, format)
        LOGGER.info(f"ExtractSub: {namafile} by {update.from_user.first_name} [{update.from_user.id}]")
        extract = (await shell_exec(f"mediaextract -i {link} -map {map} '{namafile}'"))[0]
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        c_time = time()
        await update.message.reply_document(
            namafile,
            caption=f"<b>Filename:</b> <code>{namafile}</code>\n\nExtracted by @{bot.me.username} in {timelog}",
            reply_to_message_id=usr.id,
            progress=progress_for_pyrogram,
            progress_args=("Uploading files..", update.message, c_time),
        )
        await update.message.delete()
        try:
            os.remove(namafile)
        except:
            pass
    except Exception as e:
        await update.message.edit(f"Failed extract sub, Maybe unsupported format..\n\nLink: {link}\nERR: {e}")
