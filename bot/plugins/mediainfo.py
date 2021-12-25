import io
import json
import requests
import aiohttp
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import COMMAND_HANDLER
from utils import get_file_id
from bot.utils.media_helper import post_to_telegraph, runcmd, safe_filename, get_media_info

@Client.on_message(filters.command(["mediainfo","mediainfo@MissKatyRoBot"], COMMAND_HANDLER))
async def mediainfo(_, message):
    reply = message.reply_to_message
    if not reply:
        try:
            link = message.text.split(" ", maxsplit=1)[1]
            process = await message.reply_text("`Mohon tunggu sejenak...`")
            output = await get_media_info(link)
            title = f"MissKaty Bot Mediainfo"
            media_info_file = io.BytesIO()
            media_info_file.name = "MissKaty_Mediainfo.txt"
            media_info_file.write(output)
            body_text = f"""
                         <img src='https://telegra.ph/file/72c99bbc89bbe4e178cc9.jpg' />
                         <pre>{output}</pre>
                         """
            link = post_to_telegraph(title, body_text)
            #siteurl = "https://spaceb.in/api/v1/documents/"
            #response = requests.post(siteurl, data={"content": output, "extension": 'txt'} )
            #response = response.json()
            #link = "https://spaceb.in/"+response['payload']['id']
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="💬 Link MediaInfo", url=link)]])
            await message.reply_document(media_info_file, caption="Hasil mediainfo anda..", reply_markup=markup)
            await process.delete()
        except IndexError:
            return await message.reply_text("Gunakan command /mediainfo [link], atau reply telegram media dengan /mediainfo.")
    else:
        process = await message.reply_text("`Sedang memproses, lama waktu tergantung ukuran file kamu...`")
        x_media = None
        file_info = get_file_id(message.reply_to_message)
        if file_info is None:
           await process.edit_text("Balas ke format media yang valid")
           return
        file_path = safe_filename(await reply.download())
        output_ = await runcmd(f'mediainfo "{file_path}"')
        out = None
        if len(output_) != 0:
             out = output_[0]
        body_text = f"""
    <img src='https://telegra.ph/file/72c99bbc89bbe4e178cc9.jpg' />
    <h2>JSON</h2>
    <pre>{file_info}.type</pre>
    <br>
    <h2>DETAILS</h2>
    <pre>{out or 'Not Supported'}</pre>
    """
        title = f"MissKaty Bot Mediainfo"
        text_ = file_info.message_type
        link = post_to_telegraph(title, body_text)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=text_, url=link)]])
        await process.edit_text("ℹ️ <b>MEDIA INFO</b>", reply_markup=markup)
