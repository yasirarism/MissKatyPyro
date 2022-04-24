# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os, time
from shutil import rmtree
from pyrogram import filters
from pyrogram.types import InputMediaPhoto
from bot import app
from bot.utils.ffmpeg_helper import generate_screen_shots
from info import COMMAND_HANDLER
from bot.utils.decorator import capture_err
from bot.utils.pyro_progress import (
    progress_for_pyrogram,
    humanbytes,
)

@app.on_message(filters.command(["genss","genss@MissKatyRoBot"], COMMAND_HANDLER))
@capture_err
async def genss(client, message):
    if message.reply_to_message is not None:
        process = await message.reply_text("`Processing, please wait gan/sis...`")
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            progress=progress_for_pyrogram,
            progress_args=("Trying to download, please wait..", process, c_time),
        )
        if the_real_download_location is not None:
            await client.edit_message_text(
                text=f"File video berhasil didownload dengan path <code>{the_real_download_location}</code>.\n\nMencoba mengupload hasil generate screenshot..",
                chat_id=message.chat.id,
                message_id=process.message_id
            )
            tmp_directory_for_each_user = "./MissKaty_Genss/" + str(message.from_user.id)
            if not os.path.isdir(tmp_directory_for_each_user):
                os.makedirs(tmp_directory_for_each_user)
            images = await generate_screen_shots(
                the_real_download_location,
                tmp_directory_for_each_user,
                5,
                9
            )
            logger.info(images)
            media_album_p = []
            if images is not None:
                i = 0
                caption = "© Di Generate Oleh @MissKatyRobot"
                for image in images:
                    if os.path.exists(image):
                        if i == 0:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image,
                                    caption=caption,
                                    parse_mode="html"
                                )
                            )
                        else:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
            await client.send_media_group(
                chat_id=message.chat.id,
                disable_notification=True,
                reply_to_message_id=message.message_id,
                media=media_album_p
            )
            await process.delete()
            try:
                rmtree(tmp_directory_for_each_user)
                os.remove(the_real_download_location)
            except:
                pass
    else:
        await message.reply("Reply to a Telegram media to get screenshots..")
