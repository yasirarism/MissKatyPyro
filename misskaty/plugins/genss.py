"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import math
import os
import time
from asyncio import gather, sleep
from datetime import datetime
from logging import getLogger
from urllib.parse import unquote

from pyrogram import Client, enums
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import Message
from pySmartDL import SmartDL

from misskaty import app
from misskaty.core.decorator import new_task
from misskaty.helper import is_url, progress_for_pyrogram, take_ss
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.pyro_progress import humanbytes

LOGGER = getLogger("MissKaty")

__MODULE__ = "MediaTool"
__HELP__ = """"
/genss [reply to video] - Generate Screenshot From Video. (Support TG Media and Direct URL)
/mediainfo [link/reply to TG Video] - Get Mediainfo From File.
"""


@app.on_cmd("genss")
@new_task
@use_chat_lang()
async def genss(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return
    replied = ctx.reply_to_message
    if len(ctx.command) == 2 and is_url(ctx.command[1]):
        pesan = await ctx.reply_msg(strings("wait_dl"), quote=True)
        start_t = datetime.now()
        the_url_parts = " ".join(ctx.command[1:])
        url = the_url_parts.strip()
        file_name = os.path.basename(url)
        download_file_path = os.path.join("downloads/", file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False, timeout=10, verify=False)
        try:
            downloader.start(blocking=False)
        except Exception as err:
            return await pesan.edit(str(err))
        c_time = time.time()
        while not downloader.isFinished():
            total_length = downloader.filesize or None
            downloaded = downloader.get_dl_size(human=True)
            display_message = ""
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed(human=True)
            progress_str = "[{0}{1}]\nProgress: {2}%".format(
                "".join(["●" for _ in range(math.floor(percentage / 5))]),
                "".join(["○" for _ in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )

            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = "Trying to download...\n"
                current_message += f"URL: <code>{url}</code>\n"
                current_message += f"File Name: <code>{unquote(file_name)}</code>\n"
                current_message += f"Speed: {speed}\n"
                current_message += f"{progress_str}\n"
                current_message += f"{downloaded} of {humanbytes(total_length)}\n"
                current_message += f"ETA: {estimated_total_time}"
                if round(diff % 10.00) == 0 and current_message != display_message:
                    await pesan.edit(
                        disable_web_page_preview=True, text=current_message
                    )
                    display_message = current_message
                    await sleep(10)
            except Exception as e:
                LOGGER.info(str(e))
        if os.path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await pesan.edit(
                f"Downloaded to <code>{download_file_path}</code> in {ms} seconds"
            )
            try:
                images = await take_ss(download_file_path)
                await pesan.edit_msg(strings("up_progress"))
                await self.send_chat_action(
                    chat_id=ctx.chat.id, action=enums.ChatAction.UPLOAD_PHOTO
                )
                try:
                    await gather(
                        *[
                            ctx.reply_document(images, reply_to_message_id=ctx.id),
                            ctx.reply_photo(images, reply_to_message_id=ctx.id),
                        ]
                    )
                except FloodWait as e:
                    await sleep(e.value)
                    await gather(
                        *[
                            ctx.reply_document(images, reply_to_message_id=ctx.id),
                            ctx.reply_photo(images, reply_to_message_id=ctx.id),
                        ]
                    )
                await ctx.reply_msg(
                    strings("up_msg").format(
                        namma=ctx.from_user.mention,
                        id=ctx.from_user.id,
                        bot_uname=self.me.username,
                    ),
                    reply_to_message_id=ctx.id,
                )
                await pesan.delete()
                try:
                    os.remove(images)
                    os.remove(download_file_path)
                except:
                    pass
            except Exception as exc:
                await ctx.reply_msg(strings("err_ssgen").format(exc=exc))
                try:
                    os.remove(images)
                    os.remove(download_file_path)
                except:
                    pass
    elif replied and replied.media:
        vid = [replied.video, replied.document]
        media = next((v for v in vid if v is not None), None)
        if media is None:
            return await ctx.reply_msg(strings("no_reply"), quote=True)
        process = await ctx.reply_msg(strings("wait_dl"), quote=True)
        if media.file_size > 2097152000:
            return await process.edit_msg(strings("limit_dl"))
        c_time = time.time()
        dc_id = FileId.decode(media.file_id).dc_id
        try:
            dl = await replied.download(
                file_name="downloads/",
                progress=progress_for_pyrogram,
                progress_args=(strings("dl_progress"), process, c_time, dc_id),
            )
        except FileNotFoundError:
            return await process.edit_msg("ERROR: FileNotFound.")
        the_real_download_location = os.path.join("downloads/", os.path.basename(dl))
        if the_real_download_location is not None:
            try:
                await process.edit_msg(
                    strings("success_dl_msg").format(path=the_real_download_location)
                )
                await sleep(2)
                images = await take_ss(the_real_download_location)
                await process.edit_msg(strings("up_progress"))
                await self.send_chat_action(
                    chat_id=ctx.chat.id, action=enums.ChatAction.UPLOAD_PHOTO
                )

                try:
                    await gather(
                        *[
                            ctx.reply_document(images, reply_to_message_id=ctx.id),
                            ctx.reply_photo(images, reply_to_message_id=ctx.id),
                        ]
                    )
                except FloodWait as e:
                    await sleep(e.value)
                    await gather(
                        *[
                            ctx.reply_document(images, reply_to_message_id=ctx.id),
                            ctx.reply_photo(images, reply_to_message_id=ctx.id),
                        ]
                    )
                await ctx.reply_msg(
                    strings("up_msg").format(
                        namma=ctx.from_user.mention,
                        id=ctx.from_user.id,
                        bot_uname=self.me.username,
                    ),
                    reply_to_message_id=ctx.id,
                )
                await process.delete()
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
            except Exception as exc:
                await ctx.reply_msg(strings("err_ssgen").format(exc=exc))
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
    else:
        await ctx.reply_msg(strings("no_reply"), del_in=6)
