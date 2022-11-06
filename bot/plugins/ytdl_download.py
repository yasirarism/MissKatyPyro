import os, logging
import urllib.request
from bot import app
from pyrogram import filters, enums
from info import COMMAND_HANDLER
from datetime import datetime, timedelta
from bot.core.decorator.errors import capture_err
from bot.helper.ytdl_helper import extractYt, create_buttons
from PIL import Image

LOGGER = logging.getLogger(__name__)

users ={}
user_time = {}
youtube_next_fetch = 0  # time in minute

@app.on_message(filters.command(["ytdown"], COMMAND_HANDLER))
@capture_err
async def ytdown(_, message):
    if len(message.command) == 1:
        return await message.reply(f"Gunakan command /{message.command[0]} YT_LINK untuk download video dengan YT-DLP.")
    userLastDownloadTime = user_time.get(message.chat.id)
    try:
        if userLastDownloadTime > datetime.now():
            wait_time = round((userLastDownloadTime - datetime.now()).total_seconds() / 60, 2)
            await message.reply_text(f"Wait {wait_time} Minutes before next request..")
            return
    except:
        pass

    link = message.command[1]
    await message.reply_chat_action(enums.ChatAction.TYPING)
    try:
        title, thumbnail_url, formats = extractYt(url)

        now = datetime.now()
        user_time[message.chat.id] = now + timedelta(minutes=youtube_next_fetch)

    except Exception as e:
        return await message.reply_text(f"Failed To Fetch Data... 😔\n\n{e}")
    sentm = await message.reply_text("Processing Youtube Url 🔎 🔎 🔎")
    try:
        # Todo add webp image support in thumbnail by default not supported by pyrogram
        # https://www.youtube.com/watch?v=lTTajzrSkCw
        img = urllib.request.urlretrieve(thumbnail_url)
        im = Image.open(img).convert("RGB")
        output_directory = os.path.join(os.getcwd(), "downloads", str(message.chat.id))
        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)
        thumb_image_path = f"{output_directory}.jpg"
        im.save(thumb_image_path,"jpeg")
        await message.reply_photo(thumb_image_path, caption=title, reply_markup=buttons)
        await sentm.delete()
    except Exception as e:
        LOGGER.error(e)
        try:
            thumbnail_url = "https://telegra.ph/file/ce37f8203e1903feed544.png"
            await message.reply_photo(thumbnail_url, caption=title, reply_markup=buttons)
        except Exception as e:
            await sentm.edit(f"<code>{e}</code> #Error")