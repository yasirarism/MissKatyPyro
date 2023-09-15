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
from time import time
from urllib.parse import unquote

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.misskaty_patch.listen.listen import ListenerTimeout
from misskaty.helper.human_read import get_readable_time
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.pyro_progress import progress_for_pyrogram
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


@app.on_message(filters.command(["ceksub", "extractmedia"], COMMAND_HANDLER))
@use_chat_lang()
async def ceksub(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("sub_extr_help").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    link = ctx.command[1]
    start_time = time()
    pesan = await ctx.reply_msg(strings("progress_str"), quote=True)
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
                        f"streamextract#{lang}#0:{mapping}#{stream_name}",
                    )
                ]
            )
        timelog = time() - start_time
        buttons.append(
            [InlineKeyboardButton(strings("cancel_btn"), f"close#{ctx.from_user.id}")]
        )
        msg = await pesan.edit_msg(
            strings("press_btn_msg").format(timelog=get_readable_time(timelog)),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        await msg.wait_for_click(from_user_id=ctx.from_user.id, timeout=30)
    except ListenerTimeout:
        await msg.edit_msg(strings("exp_task", context="general"))
    except Exception:
        await pesan.edit_msg(strings("fail_extr_media"))


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
        return await ctx.reply_msg(
            strings("conv_sub_help").format(cmd=ctx.command[0]), del_in=6
        )
    msg = await ctx.reply_msg(strings("convert_str"), quote=True)
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
    except:
        pass


@app.on_callback_query(filters.regex(r"^streamextract#"))
@use_chat_lang()
async def stream_extract(self: Client, update: CallbackQuery, strings):
    cb_data = update.data
    usr = update.message.reply_to_message
    if update.from_user.id != usr.from_user.id:
        return await update.answer(strings("unauth_cb"), True)
    _, lang, map_code, codec = cb_data.split("#")
    try:
        link = update.message.reply_to_message.command[1]
    except:
        return await update.answer(strings("invalid_cb"), True)
    await update.message.edit_msg(strings("progress_str"))
    if codec == "aac":
        ext = "aac"
    elif codec == "mp3":
        ext = "mp3"
    elif codec == "eac3":
        ext = "eac3"
    else:
        ext = "srt"
    start_time = time()
    namafile = get_subname(lang, link, ext)
    try:
        LOGGER.info(
            f"ExtractSub: {namafile} by {update.from_user.first_name} [{update.from_user.id}]"
        )
        (await shell_exec(f"ffmpeg -i {link} -map {map_code} '{namafile}'"))[0]
        timelog = time() - start_time
        c_time = time()
        await update.message.reply_document(
            namafile,
            caption=strings("capt_extr_sub").format(
                nf=namafile, bot=self.me.username, timelog=get_readable_time(timelog)
            ),
            reply_to_message_id=usr.id,
            thumb="assets/thumb.jpg",
            progress=progress_for_pyrogram,
            progress_args=(strings("up_str"), update.message, c_time, self.me.dc_id),
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
