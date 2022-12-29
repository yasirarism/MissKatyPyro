"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import os, time, traceback
from asyncio import sleep, gather
from shutil import rmtree
from logging import getLogger
from pyrogram import filters, enums
from pyrogram.errors import FloodWait
from misskaty import app, BOT_USERNAME
from misskaty.helper.ffmpeg_helper import take_ss, genss_link
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.pyro_progress import progress_for_pyrogram

LOGGER = getLogger(__name__)

__MODULE__ = "MediaTool"
__HELP__ = """"
/genss [reply to video] - Generate Screenshot From Video.
/genss_link [link] - Generate Screenshot Video From URL. (Unstable)
/mediainfo [link/reply to TG Video] - Get Mediainfo From File.
"""


@app.on_message(filters.command(["genss"], COMMAND_HANDLER))
@capture_err
async def genss(client, message):
    if message.reply_to_message is not None:
        process = await message.reply_text("`Processing, please wait..`")
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            progress=progress_for_pyrogram,
            progress_args=("Trying to download, please wait..", process, c_time),
        )
        if the_real_download_location is not None:
            try:
                await client.edit_message_text(
                    text=f"File video berhasil didownload dengan path <code>{the_real_download_location}</code>.",
                    chat_id=message.chat.id,
                    message_id=process.id,
                )
                await sleep(2)
                images = await take_ss(the_real_download_location)
                await client.edit_message_text(
                    text="Mencoba mengupload, hasil generate screenshot..",
                    chat_id=message.chat.id,
                    message_id=process.id,
                )
                await client.send_chat_action(
                    chat_id=message.chat.id, action=enums.ChatAction.UPLOAD_PHOTO
                )

                try:
                    await gather(
                        *[
                            message.reply_document(
                                images, reply_to_message_id=message.id
                            ),
                            message.reply_photo(images, reply_to_message_id=message.id),
                        ]
                    )
                except FloodWait as e:
                    await sleep(e.value)
                    await gather(
                        *[
                            message.reply_document(
                                images, reply_to_message_id=message.id
                            ),
                            message.reply_photo(images, reply_to_message_id=message.id),
                        ]
                    )
                await message.reply(
                    f"☑️ Uploaded [1] screenshoot.\n\n{message.from_user.first_name} (<code>{message.from_user.id}</code>)\n#️⃣ #ssgen #id{message.from_user.id}\n\nSS Generate by @{BOT_USERNAME}",
                    reply_to_message_id=message.id,
                )
                await process.delete()
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
            except Exception:
                exc = traceback.format_exc()
                await message.reply(f"Gagal generate screenshot.\n\n{exc}")
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
    else:
        await message.reply("Reply to a Telegram media to get screenshots..")


@app.on_message(filters.command(["genss_link"], COMMAND_HANDLER))
@capture_err
async def genss_link(client, message):
    try:
        link = message.text.split(" ")[1]
        if link.startswith("https://file.yasirweb.my.id"):
            link = link.replace(
                "https://file.yasirweb.my.id", "https://file.yasiraris.workers.dev"
            )
        if link.startswith("https://link.yasirweb.my.id"):
            link = link.replace(
                "https://link.yasirweb.my.id", "https://yasirrobot.herokuapp.com"
            )
        process = await message.reply_text("`Processing, please wait..`")
        tmp_directory_for_each_user = f"./MissKaty_Genss/{str(message.from_user.id)}"
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        images = await genss_link(process, link, tmp_directory_for_each_user, 5, 8)
        await sleep(2)
        await client.edit_message_text(
            text="Mencoba mengupload, hasil generate screenshot..",
            chat_id=message.chat.id,
            message_id=process.id,
        )
        await client.send_chat_action(
            chat_id=message.chat.id, action=enums.ChatAction.UPLOAD_PHOTO
        )
        try:
            await message.reply_media_group(images, reply_to_message_id=message.id)
        except FloodWait as e:
            await sleep(e.value)
            await message.reply_media_group(images, reply_to_message_id=message.id)
        await message.reply(
            f"☑️ Uploaded [8] screenshoot.\n\nGenerated by @{BOT_USERNAME}.",
            reply_to_message_id=message.id,
        )
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
