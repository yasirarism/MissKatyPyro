"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @created       2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import json
import os
from logging import getLogger
from re import I
from re import split as ngesplit
from time import perf_counter, time
from urllib.parse import unquote

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.decorator.errors import capture_err

# from misskaty.core.misskaty_patch.listen.listen import ListenerTimeout
from misskaty.helper.pyro_progress import progress_for_pyrogram
from misskaty.helper.tools import get_random_string
from misskaty.helper.localization import use_chat_lang
from misskaty.plugins.dev import shell_exec
from misskaty.vars import COMMAND_HANDLER

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
@ratelimiter
@use_chat_lang()
async def ceksub(self: Client, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(strings("sub_extr_help").format(cmd=ctx.command[0]), quote=True, del_in=5)
    link = ctx.command[1]
    start_time = perf_counter()
    pesan = await ctx.reply_msg(strings("progress_str"), quote=True)
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
        timelog = "{:.2f}".format(end_time - start_time) + strings("val_sec")
        buttons.append([InlineKeyboardButton(strings("cancel_btn"), f"close#{ctx.from_user.id}")])
        msg = await pesan.edit_msg(
            strings("press_btn_msg").format(timelog=timelog),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    #     await msg.wait_for_click(
    #         from_user_id=ctx.from_user.id,
    #         timeout=30
    #     )
    # except ListenerTimeout:
    #     await msg.edit_msg("😶‍🌫️ Timeout. Task has been cancelled!")
    except Exception:
        await pesan.edit_msg(strings("fail_extr_media"))


@app.on_message(filters.command(["converttosrt"], COMMAND_HANDLER))
@capture_err
@ratelimiter
@use_chat_lang()
async def convertsrt(self: Client, ctx: Message, strings):
    reply = ctx.reply_to_message
    if not reply and reply.document and (reply.document.file_name.endswith(".vtt") or reply.document.file_name.endswith(".ass")):
        return await ctx.reply_msg(strings("conv_sub_help").format(cmd=ctx.command[0]), del_in=5)
    msg = await ctx.reply_msg(strings("convert_str"), quote=True)
    dl = await reply.download()
    filename = dl.split("/", 3)[3]
    LOGGER.info(f"ConvertSub: {filename} by {ctx.from_user.first_name} [{ctx.from_user.id}]")
    (await shell_exec(f"mediaextract -i '{dl}' '{filename}.srt'"))[0]
    c_time = time()
    await ctx.reply_document(
        f"{filename}.srt",
        caption=strings("capt_conv_sub").format(nf=filename, bot=self.me.username),
        thumb="assets/thumb.jpg",
        progress=progress_for_pyrogram,
        progress_args=(strings("up_str"), msg, c_time),
    )
    await msg.delete_msg()
    try:
        os.remove(dl)
        os.remove(f"{filename}.srt")
    except:
        pass


@app.on_callback_query(filters.regex(r"^streamextract#"))
@ratelimiter
@use_chat_lang()
async def stream_extract(self: Client, update: CallbackQuery, strings):
    cb_data = update.data
    usr = update.message.reply_to_message
    if update.from_user.id != usr.from_user.id:
        return await update.answer(strings("unauth_cb"), True)
    _, lang, map, codec = cb_data.split("#")
    try:
        link = update.message.reply_to_message.command[1]
    except:
        return await update.answer(strings("invalid_cb"), True)
    await update.message.edit_msg(strings("progress_str"))
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
    try:
        LOGGER.info(f"ExtractSub: {namafile} by {update.from_user.first_name} [{update.from_user.id}]")
        (await shell_exec(f"mediaextract -i {link} -map {map} '{namafile}'"))[0]
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + strings("val_sec")
        c_time = time()
        await update.message.reply_document(
            namafile,
            caption=strings("capt_extr_sub").format(nf=namafile, bot=self.me.username, timelog=timelog),
            reply_to_message_id=usr.id,
            thumb="assets/thumb.jpg",
            progress=progress_for_pyrogram,
            progress_args=(strings("up_str"), update.message, c_time),
        )
        await update.message.delete_msg()
        try:
            os.remove(namafile)
        except:
            pass
    except Exception as e:
        try:
            os.remove(namafile)
        except:
            pass
        await update.message.edit_msg(strings("fail_extr_sub").format(link=link, e=e))
