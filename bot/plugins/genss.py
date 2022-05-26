# the logging things
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os, time
from asyncio import sleep
from shutil import rmtree
from pyrogram import filters
from pyrogram.types import InputMediaPhoto
from pyrogram.errors import FloodWait
from bot import app
from bot.utils.ffmpeg_helper import generate_screen_shots
from info import COMMAND_HANDLER
from bot.utils.decorator import capture_err
from bot.utils.pyro_progress import (
    progress_for_pyrogram,
    humanbytes,
)


@app.on_message(
    filters.command(["genss", "genss@MissKatyRoBot"], COMMAND_HANDLER))
@capture_err
async def genss(client, message):
    if len(message.command) > 1 and message.command[1].isdigit():
        sscount = int(message.command[1])
    else:
        sscount = 9

    if message.reply_to_message is not None:
        process = await message.reply_text(
            f"`Processing, please wait {message.from_user.first_name}...`")
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            progress=progress_for_pyrogram,
            progress_args=("Trying to download, please wait..", process,
                           c_time),
        )
        if the_real_download_location is not None:
            try:
                await client.edit_message_text(
                    text=
                    f"File video berhasil didownload dengan path <code>{the_real_download_location}</code>.",
                    chat_id=message.chat.id,
                    message_id=process.id)
            except FloodWait as e:
                await sleep(e.x)
                await client.edit_message_text(
                    text=
                    f"File video berhasil didownload dengan path <code>{the_real_download_location}</code>.",
                    chat_id=message.chat.id,
                    message_id=process.id)
            tmp_directory_for_each_user = "./MissKaty_Genss/" + str(
                message.from_user.id)
            if not os.path.isdir(tmp_directory_for_each_user):
                os.makedirs(tmp_directory_for_each_user)
            images = await generate_screen_shots(the_real_download_location,
                                                 tmp_directory_for_each_user,
                                                 5, sscount)
            # logger.info(images)
            try:
                await client.edit_message_text(
                    text="Mencoba mengupload, hasil generate screenshot..",
                    chat_id=message.chat.id,
                    message_id=process.id)
            except FloodWait as e:
                await sleep(e.value)
                await client.edit_message_text(
                    text="Mencoba mengupload, hasil generate screenshot..",
                    chat_id=message.chat.id,
                    message_id=process.id)
            media_album_p = []
            if images is not None:
                i = 0
                caption = "© Di Generate Oleh @MissKatyRobot"
                for image in images:
                    if os.path.exists(image):
                        if i == 0:
                            media_album_p.append(
                                InputMediaPhoto(media=image, caption=caption))
                        else:
                            media_album_p.append(InputMediaPhoto(media=image))
                        i = i + 1
            try:
                await client.send_media_group(chat_id=message.chat.id,
                                              disable_notification=True,
                                              reply_to_message_id=message.id,
                                              media=media_album_p)
            except FloodWait as e:
                await sleep(e.value)
                await client.send_media_group(chat_id=message.chat.id,
                                              disable_notification=True,
                                              reply_to_message_id=message.id,
                                              media=media_album_p)
            await client.delete_messages(chat_id=message.chat.id,
                                         message_ids=process.id)
            try:
                rmtree(tmp_directory_for_each_user)
                os.remove(the_real_download_location)
            except:
                pass
    else:
        await message.reply("Reply to a Telegram media to get screenshots..")
