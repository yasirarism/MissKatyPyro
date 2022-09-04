# the logging things
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

import os, time, traceback
from asyncio import sleep
from shutil import rmtree
from pyrogram import filters, enums
from pyrogram.errors import FloodWait
from bot import app
from bot.utils.ffmpeg_helper import generate_screen_shots, genss_link
from info import COMMAND_HANDLER
from bot.utils.pyro_progress import (
    progress_for_pyrogram, )

__MODULE__ = "GenSS"
__HELP__ = "/genss - Generate Screenshot From Video"


@app.on_message(filters.command(["genss"], COMMAND_HANDLER))
async def genss(client, message):
    if len(message.command) > 1 and message.command[1].isdigit():
        sscount = int(message.command[1])
    else:
        sscount = 8
    if message.reply_to_message is not None:
        process = await message.reply_text("`Processing, please wait..`")
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            progress=progress_for_pyrogram,
            progress_args=("Trying to download, please wait..", process,
                           c_time))

        await sleep(2)
        if the_real_download_location is not None:
            try:
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

                tmp_directory_for_each_user = f"./MissKaty_Genss/{str(message.from_user.id)}"
                if not os.path.isdir(tmp_directory_for_each_user):
                    os.makedirs(tmp_directory_for_each_user)
                images = await generate_screen_shots(
                    process, the_real_download_location,
                    tmp_directory_for_each_user, 5, sscount)

                await sleep(3)
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

                await client.send_chat_action(
                    chat_id=message.chat.id,
                    action=enums.ChatAction.UPLOAD_PHOTO)

                try:
                    await message.reply_media_group(
                        images, reply_to_message_id=message.id)
                except FloodWait as e:
                    await sleep(e.value)
                    await message.reply_media_group(
                        images, reply_to_message_id=message.id)
                try:
                    await message.reply(
                        f"☑️ Uploaded [{sscount}] screenshoot.\n\nGenerated by @MissKatyRoBot.",
                        reply_to_message_id=message.id)

                except FloodWait as e:
                    await sleep(e.value)
                    await message.reply(
                        f"☑️ Uploaded [{sscount}] screenshoot.\n\nGenerated by @MissKatyRoBot.",
                        reply_to_message_id=message.id)

                await process.delete()
                try:
                    rmtree(tmp_directory_for_each_user)
                    os.remove(the_real_download_location)
                except:
                    pass
            except Exception:
                exc = traceback.format_exc()
                await message.reply(f"Gagal generate screenshot.\n\n{exc}")
                try:
                    rmtree(tmp_directory_for_each_user)
                    os.remove(the_real_download_location)
                except:
                    pass
    else:
        await message.reply("Reply to a Telegram media to get screenshots..")


@app.on_message(filters.command(["genss_link"], COMMAND_HANDLER))
async def genss(client, message):
    try:
        link = message.text.split(" ")[1]
        if link.startswith("https://file.yasirweb.my.id"):
            link = link.replace("https://file.yasirweb.my.id",
                                "https://file.yasiraris.workers.dev")
        if link.startswith("https://link.yasirweb.my.id"):
            link = link.replace("https://link.yasirweb.my.id",
                                "https://yasirrobot.herokuapp.com")
        process = await message.reply_text("`Processing, please wait..`")
        tmp_directory_for_each_user = f"./MissKaty_Genss/{str(message.from_user.id)}"
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        images = await genss_link(process, link, tmp_directory_for_each_user,
                                  5, 8)
        await sleep(3)
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
        await client.send_chat_action(chat_id=message.chat.id,
                                      action=enums.ChatAction.UPLOAD_PHOTO)
        try:
            await message.reply_media_group(images,
                                            reply_to_message_id=message.id)
        except FloodWait as e:
            await sleep(e.value)
            await message.reply_media_group(images,
                                            reply_to_message_id=message.id)
        try:
            await message.reply(
                f"☑️ Uploaded [8] screenshoot.\n\nGenerated by @MissKatyRoBot.",
                reply_to_message_id=message.id)
        except FloodWait as e:
            await sleep(e.value)
            await message.reply(
                f"☑️ Uploaded [8] screenshoot.\n\nGenerated by @MissKatyRoBot.",
                reply_to_message_id=message.id)
        await process.delete()
        try:
            rmtree(tmp_directory_for_each_user)
        except:
            pass
    except Exception:
        exc = traceback.format_exc()
        await message.reply(f"Gagal generate screenshot.\n\n{exc}")
        try:
            rmtree(tmp_directory_for_each_user)
        except:
            pass
