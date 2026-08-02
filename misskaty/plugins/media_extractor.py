"""
* @author        yasir <yasiramunandar@gmail.com>
* @created       2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

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
    fragment_removed = url.split("#")[0]
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1 or not get_base_name(
        os.path.basename(unquote(scheme_removed))
    ):
        return f"[{lang.upper()}] MissKatySub{get_random_string(4)}.{ext}"
    return f"[{lang.upper()}] {get_base_name(os.path.basename(unquote(scheme_removed)))}{get_random_string(3)}.{ext}"


class MediaExtractor:
    def __init__(self, client: Client, message: Message | None = None, callback: CallbackQuery | None = None, strings=None) -> None:
        self.client = client
        self.message = message
        self.callback = callback
        self.strings = strings

    async def _reply(self, text: str, *args, **kwargs):
        if self.callback:
            return await self.callback.answer(text, *args, **kwargs)
        if self.message:
            return await self.message.reply_text(text, *args, **kwargs)
        return None

    async def _edit(self, text: str, *args, **kwargs):
        target = getattr(self.callback, "message", None) or self.message
        if not target:
            return None
        return await target.edit_text(text, *args, **kwargs)

    async def _progress_reply(self, text: str):
        if self.callback:
            return await self.callback.message.edit(text)
        return await self.message.reply_text(text)

    async def _delete_progress(self):
        if self.callback and self.callback.message:
            with contextlib.suppress(Exception):
                await self.callback.message.delete()
        elif self.message:
            with contextlib.suppress(Exception):
                await self.message.delete()

    def _is_authorized(self, user_id: int) -> bool:
        if self.callback:
            usr = self.callback.message.reply_to_message
            if not usr or not usr.from_user:
                return False
            return user_id == usr.from_user.id
        return True

    def _get_source_link(self) -> str | None:
        if self.callback:
            try:
                return self.callback.message.reply_to_message.command[1]
            except Exception:
                return None
        if self.message:
            try:
                return self.message.command[1]
            except Exception:
                return None
        return None

    async def analyze(self, link: str):
        try:
            res = (await shell_exec(f"ffprobe -loglevel 0 -print_format json -show_format -show_streams {link}"))[0]
            details = json.loads(res)
            buttons = []
            for stream in details.get("streams", []):
                mapping = stream.get("index", "?")
                stream_name = stream.get("codec_name", "-")
                stream_type = stream.get("codec_type", "")
                if stream_type not in ("audio", "subtitle"):
                    continue
                lang = stream.get("tags", {}).get("language", str(mapping))
                safe_lang = str(lang).replace("#", "_")
                safe_codec = str(stream_name).replace("#", "_")
                callback_data = f"streamextract#{safe_lang}#0:{mapping}#{safe_codec}"
                buttons.append([
                    InlineKeyboardButton(
                        f"0:{mapping}({lang}): {stream_type}: {stream_name}",
                        callback_data,
                    )
                ])
            buttons.append([
                InlineKeyboardButton(self.strings("cancel_btn"), f"close#{self.message.from_user.id if self.message and self.message.from_user else 'unknown'}")
            ])
            return buttons
        except Exception as e:
            LOGGER.error(f"Analyze media failed: {e}")
            raise

    async def extract(self, map_code: str, lang: str, codec: str, link: str):
        ext = {
            "aac": "aac",
            "mp3": "mp3",
            "eac3": "eac3",
        }.get(codec, "srt")
        namafile = get_subname(lang, link, ext)
        start_time = time()
        try:
            LOGGER.info(f"ExtractSub: {namafile} by {self.callback.from_user.first_name} [{self.callback.from_user.id}]")
            await shell_exec(f"ffmpeg -i {link} -map {map_code} '{namafile}'")
            timelog = time() - start_time
            c_time = time()
            usr = self.callback.message.reply_to_message
            await self.callback.message.reply_document(
                namafile,
                caption=self.strings("capt_extr_sub").format(
                    nf=namafile, bot=self.client.me.username, timelog=get_readable_time(timelog)
                ),
                reply_parameters=pyro_types.ReplyParameters(message_id=usr.id),
                thumb="assets/thumb.jpg",
                progress=progress_for_pyrogram,
                progress_args=(self.strings("up_str"), self.callback.message, c_time, self.client.me.dc_id),
            )
            await self._delete_progress()
        except Exception as e:
            with contextlib.suppress(Exception):
                os.remove(namafile)
            await self._edit(self.strings("fail_extr_sub").format(link=link, e=e))
