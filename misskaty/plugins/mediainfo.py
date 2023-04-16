"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import io
import subprocess
import time
from os import remove as osremove, path

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import progress_for_pyrogram, runcmd, post_to_telegraph
from misskaty.helper.mediainfo_paste import mediainfo_paste
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER
from utils import get_file_id


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def mediainfo(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return
    if ctx.reply_to_message and ctx.reply_to_message.media:
        process = await ctx.reply_msg(strings("processing_text"), quote=True)
        file_info = get_file_id(ctx.reply_to_message)
        if file_info is None:
            return await process.edit_msg(strings("media_invalid"))
        if (ctx.reply_to_message.video and ctx.reply_to_message.video.file_size > 2097152000) or (ctx.reply_to_message.document and ctx.reply_to_message.document.file_size > 2097152000):
            return await process.edit_msg(strings("dl_limit_exceeded"), del_in=6)
        c_time = time.time()
        dl = await ctx.reply_to_message.download(
            file_name="/downloads/",
            progress=progress_for_pyrogram,
            progress_args=(strings("dl_args_text"), process, c_time),
        )
        file_path = path.join("/downloads/", path.basename(dl))
        output_ = await runcmd(f'mediainfo "{file_path}"')
        out = output_[0] if len(output_) != 0 else None
        body_text = f"""
MissKatyBot MediaInfo
JSON
{file_info}.type
    
DETAILS
{out or 'Not Supported'}
    """
        file_info.message_type
        try:
            link = await mediainfo_paste(out, "MissKaty Mediainfo")
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("viweb"), url=link)]])
        except:
            try:
                link = await post_to_telegraph(False, "MissKaty MediaInfo", body_text)
                markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("viweb"), url=link)]])
            except:
                markup = None
        with io.BytesIO(str.encode(body_text)) as out_file:
            out_file.name = "MissKaty_Mediainfo.txt"
            await ctx.reply_document(
                out_file,
                caption=strings("capt_media").format(ment=ctx.from_user.mention),
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
            process = await ctx.reply_msg(strings("wait_msg"))
            try:
                output = subprocess.check_output(["mediainfo", f"{link}"]).decode("utf-8")
            except Exception:
                return await process.edit_msg(strings("err_link"))
            body_text = f"""
            MissKatyBot MediaInfo
            {output}
            """
            # link = await post_to_telegraph(False, title, body_text)
            try:
                link = await mediainfo_paste(out, "MissKaty Mediainfo")
                markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("viweb"), url=link)]])
            except:
                try:
                    link = await post_to_telegraph(False, "MissKaty MediaInfo", body_text)
                    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("viweb"), url=link)]])
                except:
                    markup = None
            with io.BytesIO(str.encode(output)) as out_file:
                out_file.name = "MissKaty_Mediainfo.txt"
                await ctx.reply_document(
                    out_file,
                    caption=strings("capt_media").format(ment=ctx.from_user.mention),
                    thumb="assets/thumb.jpg",
                    reply_markup=markup,
                )
                await process.delete()
        except IndexError:
            return await ctx.reply_msg(strings("mediainfo_help").format(cmd=ctx.command[0]), del_in=6)
