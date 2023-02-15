from importlib.resources import contents
import json
import os
import re
import subprocess
import time
from urllib.parse import unquote

import requests
from pyrogram import filters

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import (SUPPORTED_URL_REGEX, post_to_telegraph,
                             progress_for_pyrogram, runcmd)
from misskaty.vars import COMMAND_HANDLER
from utils import get_file_id


async def ddl_mediainfo(_, message, url):
    """
    Generates Mediainfo from a Direct Download Link.
    """

    try:
        filename = re.search(".+/(.+)", url).group(1)
        reply_msg = await kirimPesan(message, "Generating Mediainfo, Please wait..", quote=True)

        with requests.get(url, stream=True) as r:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(50000000): f.write(chunk); break

        output_ = await runcmd(f'mediainfo "{filename}"')
        out = output_[0] if len(output_) != 0 else None
        content = f"""
MissKatyBot MediaInfo
    
DETAILS
{out or 'Not Supported'}
    """
        output = await post_to_telegraph(False, "MissKaty MediaInfo", content)

        await editPesan(reply_msg, f"**File Name :** `{unquote(filename)}`\n\n**Mediainfo :** {output}", disable_web_page_preview=True)
        os.remove(filename)

    except Exception as err:
        await hapusPesan(reply_msg)
        await kirimPesan(message, f"Something went wrong while generating Mediainfo from the given url.\n\nERR: {err}", quote=True)


async def telegram_mediainfo(client, message):
    """
    Generates Mediainfo from a Telegram File.
    """

    replymsg = message.reply_to_message

    if replymsg.text:
        return await kirimPesan(message, "Reply to a proper media file for generating Mediainfo.**", quote=True)

    elif replymsg.media.value == 'video':
        media = replymsg.video

    elif replymsg.media.value == 'audio':
        media = replymsg.audio

    elif replymsg.media.value == 'document':
        media = replymsg.document

    elif replymsg.media.value == 'voice':
        media = replymsg.voice

    else:
        return await kirimPesan(message, "This type of media is not supported for generating Mediainfo.**", quote=True)

    filename = str(media.file_name)
    mime = media.mime_type
    size = media.file_size

    reply_msg = await kirimPesan(message, "Generating Mediainfo, Please wait..", quote=True)

    if int(size) <= 50000000:
        c_time = time.time()
        await message.download(
            os.path.join(os.getcwd(), filename),
            progress=progress_for_pyrogram,
            progress_args=("Trying to download..", reply_msg, c_time)
        )

    else:
        async for chunk in client.stream_media(message, limit=5):
            with open(filename, 'ab') as f:
                f.write(chunk)

    try:
        output_ = await runcmd(f'mediainfo "{filename}"')
        out = output_[0] if len(output_) != 0 else None
        file_info = get_file_id(message.reply_to_message)
        content = f"""
MissKatyBot MediaInfo
JSON
{file_info}.type
    
DETAILS
{out or 'Not Supported'}
    """
        output = await post_to_telegraph(False, "MissKaty MediaInfo", content)

        await editPesan(reply_msg, f"**File Name :** `{filename}`\n\n**Mediainfo :** {output}", disable_web_page_preview=True)
        os.remove(filename)

    except Exception as err:
        await hapusPesan(reply_msg)
        await kirimPesan(message, f"Something went wrong while generating Mediainfo of replied Telegram file.\n\nERR: {err}", quote=True)


@ratelimiter
@app.on_message(filters.command("mediainfo2", COMMAND_HANDLER))
async def mediainfo(client, message):
    mediainfo_usage = f"**Generate mediainfo from Telegram files or direct download links. Reply to any telegram file or just pass the link after the command."
    
    if message.reply_to_message:
        return await telegram_mediainfo(client, message)

    elif len(message.command) < 2:
        return await kirimPesan(message, mediainfo_usage, quote=True)

    user_url = message.text.split(None, 1)[1].split(" ")[0]
    for (key, value) in SUPPORTED_URL_REGEX.items():
        if bool(re.search(FR"{key}", user_url)):
            if value == "ddl":
                return await ddl_mediainfo(client, message, url=user_url)
    await kirimPesan(message, "This type of URL is not supported.", quote=True)