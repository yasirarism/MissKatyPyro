"""
* @author        yasir <yasiramunandar@gmail.com>
* @date          2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

import io
import subprocess
import time
from os import path
from os import remove as osremove

from pyrogram import filters
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import app
from misskaty.helper import post_to_telegraph, progress_for_pyrogram, runcmd
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.mediainfo_paste import mediainfo_paste
from misskaty.vars import COMMAND_HANDLER
from misskaty.helper.chat_utils import get_file_id


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
@use_chat_lang()
async def mediainfo(_, ctx: Message, strings):
    if ctx.reply_to_message and ctx.reply_to_message.media:
        process = await ctx.reply(strings("processing_text"))
        file_info = get_file_id(ctx.reply_to_message)
        if file_info is None:
            return await process.edit(strings("media_invalid"))
        if (
            ctx.reply_to_message.video
            and ctx.reply_to_message.video.file_size > 2097152000
        ) or (
            ctx.reply_to_message.document
            and ctx.reply_to_message.document.file_size > 2097152000
        ):
            return await process.edit(strings("dl_limit_exceeded"), del_in=6)
        c_time = time.time()
        dc_id = FileId.decode(file_info.file_id).dc_id
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
<pre>{file_info}.type</pre>
    
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
