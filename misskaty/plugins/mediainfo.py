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

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import progress_for_pyrogram, runcmd, post_to_telegraph
from misskaty.helper.mediainfo_paste import mediainfo_paste
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER
from utils import get_file_id


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def mediainfo(client, message, strings):
    if not message.from_user:
        return
    if message.reply_to_message and message.reply_to_message.media:
        process = await kirimPesan(message, strings("processing_text"), quote=True)
        file_info = get_file_id(message.reply_to_message)
        if file_info is None:
            return await editPesan(process, strings("media_invalid"))
        if (message.reply_to_message.video and message.reply_to_message.video.file_size > 2097152000) or (message.reply_to_message.document and message.reply_to_message.document.file_size > 2097152000):
            return await editPesan(process, strings("dl_limit_exceeded"))
        c_time = time.time()
        dl = await message.reply_to_message.download(
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
            await message.reply_document(
                out_file,
                caption=strings("capt_media").format(ment=message.from_user.mention),
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
            link = message.text.split(" ", maxsplit=1)[1]
            process = await kirimPesan(message, strings("wait_msg"))
            try:
                output = subprocess.check_output(["mediainfo", f"{link}"]).decode("utf-8")
            except Exception:
                return await editPesan(process, strings("err_link"))
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
                await message.reply_document(
                    out_file,
                    caption=strings("capt_media").format(ment=message.from_user.mention),
                    thumb="assets/thumb.jpg",
                    reply_markup=markup,
                )
                await process.delete()
        except IndexError:
            return await kirimPesan(message, strings("mediainfo_help").format(cmd=message.command[0]))
