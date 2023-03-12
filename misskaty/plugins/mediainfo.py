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
from misskaty.helper import http, progress_for_pyrogram, runcmd, post_to_telegraph
from misskaty.helper.mediainfo_paste import mediainfo_paste
from misskaty.vars import COMMAND_HANDLER
from utils import get_file_id


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
@ratelimiter
async def mediainfo(client, message):
    if not message.from_user:
        return
    if message.reply_to_message and message.reply_to_message.media:
        process = await kirimPesan(message, "`Processing, total time is based size of your files...`", quote=True)
        file_info = get_file_id(message.reply_to_message)
        if file_info is None:
            return await editPesan(process, "Please reply to valid media.")

        c_time = time.time()
        dl = await message.reply_to_message.download(
            file_name="/downloads/",
            progress=progress_for_pyrogram,
            progress_args=("Trying to download..", process, c_time),
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
        text_ = file_info.message_type
        try:
            link = await mediainfo_paste(out, "MissKaty Mediainfo")
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 View in Web", url=link)]])
        except:
            try:
                link = await post_to_telegraph(False, "MissKaty MediaInfo", body_text)
                markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 View in Web", url=link)]])
            except:
                markup = None
        with io.BytesIO(str.encode(body_text)) as out_file:
            out_file.name = "MissKaty_Mediainfo.txt"
            await message.reply_document(
                out_file,
                caption=f"ℹ️ <b>MEDIA INFO</b>\n\n**Request by:** {message.from_user.mention}",
                thumb="img/thumb.jpg",
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
            process = await kirimPesan(message, "`Mohon tunggu sejenak...`")
            try:
                output = subprocess.check_output(["mediainfo", f"{link}"]).decode("utf-8")
            except Exception:
                return await editPesan(process, "Sepertinya link yang kamu kirim tidak valid, pastikan direct link dan bisa di download.")
            body_text = f"""
            MissKatyBot MediaInfo
            {output}
            """
            # link = await post_to_telegraph(False, title, body_text)
            try:
                link = await mediainfo_paste(out, "MissKaty Mediainfo")
                markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 View in Web", url=link)]])
            except:
                try:
                    link = await post_to_telegraph(False, "MissKaty MediaInfo", body_text)
                    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 View in Web", url=link)]])
                except:
                    markup = None
            with io.BytesIO(str.encode(output)) as out_file:
                out_file.name = "MissKaty_Mediainfo.txt"
                await message.reply_document(
                    out_file,
                    caption=f"Hasil mediainfo anda..\n\n**Request by:** {message.from_user.mention}",
                    thumb="img/thumb.jpg",
                    reply_markup=markup,
                )
                await process.delete()
        except IndexError:
            return await kirimPesan(message, "Gunakan command /mediainfo [link], atau reply telegram media dengan /mediainfo.")
