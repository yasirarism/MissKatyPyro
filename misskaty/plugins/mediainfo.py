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
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app, DL_TASK
from misskaty.helper.html_view import getMediaWeb
from misskaty.helper.media_helper import post_to_telegraph, runcmd
from misskaty.helper.pyro_progress import progress_for_pyrogram
from misskaty.vars import COMMAND_HANDLER, CUSTOM_VIEW, GH_TOKEN
from utils import get_file_id


@app.on_message(filters.command(["mediainfo"], COMMAND_HANDLER))
async def mediainfo(client, message):
    if message.reply_to_message and message.reply_to_message.media:
        process = await message.reply_text("`Sedang memproses, lama waktu tergantung ukuran file kamu...`", quote=True)
        file_info = get_file_id(message.reply_to_message)
        if file_info is None:
            return await process.edit_text("Balas ke format media yang valid")
        
        if DL_TASK.get(message.from_user.id):
            return await process.edit("Sorry to avoid flood and error, bot only process one task per user at a time.")
        if not DL_TASK.get(message.from_user.id):
            DL_TASK[message.from_user.id] = 1
        
        c_time = time.time()
        file_path = await message.reply_to_message.download(
            progress=progress_for_pyrogram,
            progress_args=("trying to download, sabar yakk..", process, c_time),
        )
        output_ = await runcmd(f'mediainfo "{file_path}"')
        out = output_[0] if len(output_) != 0 else None
        body_text = f"""
    <img src='https://telegra.ph/file/72c99bbc89bbe4e178cc9.jpg' />
    <h2>JSON</h2>
    <pre>{file_info}.type</pre>
    <br>
    <h2>DETAILS</h2>
    <pre>{out or 'Not Supported'}</pre>
    """
        title = "MissKaty Bot Mediainfo"
        text_ = file_info.message_type
        if CUSTOM_VIEW and GH_TOKEN is not None:
            link = await getMediaWeb(title, body_text)
            if not link:
                try:
                    osremove(file_path)
                except:
                    pass
                return await message.reply("Failed to post mediainfo result.")
        else:
            link = post_to_telegraph(title, body_text)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=text_, url=link)]])
        try:
            await message.reply("ℹ️ <b>MEDIA INFO</b>", reply_markup=markup, quote=True)
        except FloodWait as f:
            await asyncio.sleep(f.value)
        del DL_TASK[message.from_user.id]
        await process.delete()
        try:
            osremove(file_path)
        except Exception:
            pass
    else:
        try:
            link = message.text.split(" ", maxsplit=1)[1]
            process = await message.reply_text("`Mohon tunggu sejenak...`")
            try:
                output = subprocess.check_output(["mediainfo", f"{link}"]).decode("utf-8")
            except Exception:
                return await process.edit("Sepertinya link yang kamu kirim tidak valid, pastikan direct link dan bisa di download.")
            title = "MissKaty Bot Mediainfo"
            if CUSTOM_VIEW and GH_TOKEN is not None:
                body_text = f"<code style='color:#22c1c3;'>{output}</code>"
                link = await getMediaWeb(title, body_text)
                if not link:
                    return await message.reply("Failed to post mediainfo result.")
            else:
                body_text = f"""
                    <pre>{output}</pre>
                    """
                link = post_to_telegraph(title, body_text)
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
            return await message.reply_text("Gunakan command /mediainfo [link], atau reply telegram media dengan /mediainfo.")
