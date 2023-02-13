"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import asyncio
import io
import subprocess
import time
from os import remove as osremove

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.pyro_cooldown import wait
from misskaty.helper import post_to_telegraph, runcmd, progress_for_pyrogram
from misskaty.vars import COMMAND_HANDLER
from utils import get_file_id


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER) & wait(30))
async def mediainfo(client, message):
    if not m.from_user: return
    if message.reply_to_message and message.reply_to_message.media:
        process = await kirimPesan(message, "`Sedang memproses, lama waktu tergantung ukuran file kamu...`", quote=True)
        file_info = get_file_id(message.reply_to_message)
        if file_info is None:
            return await editPesan(process, "Balas ke format media yang valid")
        
        c_time = time.time()
        file_path = await message.reply_to_message.download(
            progress=progress_for_pyrogram,
            progress_args=("trying to download, sabar yakk..", process, c_time),
        )
        output_ = await runcmd(f'mediainfo "{file_path}"')
        out = output_[0] if len(output_) != 0 else None
        body_text = f"""
    <img src='https://telegra.ph/file/72c99bbc89bbe4e178cc9.jpg' />
    <b>JSON</b>
    <pre>{file_info}.type</pre>
    <br>
    <b>DETAILS</b>
    <pre>{out or 'Not Supported'}</pre>
    """
        title = "MissKaty Bot Mediainfo"
        text_ = file_info.message_type
        link = await post_to_telegraph(False, title, body_text)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=text_, url=link)]])
        await kirimPesan(message, "ℹ️ <b>MEDIA INFO</b>", reply_markup=markup, quote=True)
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
            title = "MissKaty Bot Mediainfo"
            body_text = f"""
                    <pre>{output}</pre>
                    """
            link = await post_to_telegraph(False, title, body_text)
            # siteurl = "https://spaceb.in/api/v1/documents/"
            # response = await http.post(siteurl, data={"content": output, "extension": 'txt'} )
            # response = response.json()
            # spacebin = "https://spaceb.in/"+response['payload']['id']
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 Telegraph", url=link)]])
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
