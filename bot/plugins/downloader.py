import time
import asyncio
import math
import os
import logging
import aiohttp
import json
from bot.helper.http import http
from bs4 import BeautifulSoup
from bot import app
from pySmartDL import SmartDL
from datetime import datetime
from bot.core.decorator.errors import capture_err
from info import COMMAND_HANDLER
from pyrogram import filters
from bot.helper.pyro_progress import (
    progress_for_pyrogram,
    humanbytes,
)

__MODULE__ = "Downloader"
__HELP__ = """
/download [url] - Download file from URL (Sudo Only)
/download [reply_to_TG_File] - Download TG File
/tiktokdl [link] - Download TikTok Video
"""

@app.on_message(filters.command(["download"], COMMAND_HANDLER) & filters.user([617426792, 2024984460]))
@capture_err
async def download(client, message):
    pesan = await message.reply_text("Processing...", quote=True)
    if message.reply_to_message is not None:
        start_t = datetime.now()
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            progress=progress_for_pyrogram,
            progress_args=("trying to download, sabar yakk..", pesan, c_time),
        )
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await pesan.edit(f"Downloaded to <code>{the_real_download_location}</code> in <u>{ms}</u> seconds.")
    elif len(message.command) > 1:
        start_t = datetime.now()
        the_url_parts = " ".join(message.command[1:])
        url = the_url_parts.strip()
        custom_file_name = os.path.basename(url)
        if "|" in the_url_parts:
            url, custom_file_name = the_url_parts.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()
        download_file_path = os.path.join("downloads/", custom_file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False)
        downloader.start(blocking=False)
        c_time = time.time()
        while not downloader.isFinished():
            total_length = downloader.filesize if downloader.filesize else None
            downloaded = downloader.get_dl_size()
            display_message = ""
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed()
            round(diff) * 1000
            progress_str = "[{0}{1}]\nProgress: {2}%".format(
                "".join(["█" for i in range(math.floor(percentage / 5))]),
                "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )
            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = "trying to download...\n"
                current_message += f"URL: <code>{url}</code>\n"
                current_message += f"File Name: <code>{custom_file_name}</code>\n"
                current_message += f"Speed: {speed}\n"
                current_message += f"{progress_str}\n"
                current_message += f"{humanbytes(downloaded)} of {humanbytes(total_length)}\n"
                current_message += f"ETA: {estimated_total_time}"
                if round(diff % 10.00) == 0 and current_message != display_message:
                    await pesan.edit(disable_web_page_preview=True, text=current_message)
                    display_message = current_message
                    await asyncio.sleep(10)
            except Exception as e:
                logging.info(str(e))
        if os.path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await pesan.edit(f"Downloaded to <code>{download_file_path}</code> in {ms} seconds")
    else:
        await pesan.edit("Reply to a Telegram Media, to download it to my local server.")

@app.on_message(filters.command(["tiktokdl"], COMMAND_HANDLER))
@capture_err
async def tiktokdl(client, message):
    if len(message.command) == 1:
        return await message.reply(
            "Use command /{message.command[0]} [link] to download tiktok video.")
    link = message.command[1]
    try:
        async with aiohttp.ClientSession() as ses:
            async with ses.get(
                    f"https://api.hayo.my.id/api/tiktok/4?url={link}"
            ) as result:
                r = await result.json()
                await message.reply_video(
                    r["linkori"],
                    caption=
                    f"<b>Title:</b> <code>{r['name']}</code>\n\nUploaded for {message.from_user.mention} [{<code>message.from_user.id</code>}]"
                )
    except Exception as e:
        await message.reply(
            f"Failed to download tiktok video..\n\n<b>Reason:</b> {e}")

@app.on_message(filters.command(["fbdl"], COMMAND_HANDLER))
@capture_err
async def fbdl(client, message):
    if len(message.command) == 1:
        return await message.reply(f"Use command /{message.command[0]} [link] to download tiktok video.")
    link = message.command[1]
    try:
        r = await http.post("https://yt1s.io/api/ajaxSearch/facebook", data={"q": link,"vt": "facebook"}).text
        bs = BeautifulSoup(r, "lxml")
        resjson = json.loads(str(bs).replace("<html><body><p>", "").replace("</p></body></html>",""))
        try:
            url = resjson['links']['hd']
        except:
            url = resjson['links']['sd']
        obj = SmartDL(url, progress_bar=False)
        obj.start()
        path = obj.get_dest()
        await message.reply_video(path)
        try:
            os.remove(path)
        except:
            pass
    except Exception as e:
        await message.reply(f"Failed to download Facebook video..\n\n<b>Reason:</b> {e}")