import json
import os
import re
import time
import subprocess
from urllib.parse import unquote

import requests
from pyrogram import filters

from misskaty import app
from misskaty.helper import (SUPPORTED_URL_REGEX, get_readable_bitrate,
                             get_readable_file_size, post_to_telegraph,
                             progress_for_pyrogram, remove_N)
from misskaty.vars import COMMAND_HANDLER


async def ddl_mediainfo(_, message, url):
    """
    Generates Mediainfo from a Direct Download Link.
    """

    try:
        filename = re.search(".+/(.+)", url).group(1)
        reply_msg = await message.reply_text("Generating Mediainfo, Please wait..", quote=True)

        with requests.get(url, stream=True) as r:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(50000000): f.write(chunk); break

        mediainfo = subprocess.check_output(['mediainfo', filename]).decode("utf-8")
        mediainfo_json = json.loads(subprocess.check_output(['mediainfo', filename, '--Output=JSON']).decode("utf-8"))

        filesize = requests.head(url).headers.get('content-length')

        lines = mediainfo.splitlines()
        for i in range(len(lines)):
            if 'Complete name' in lines[i]:
                lines[i] = re.sub(r": .+", ': ' + unquote(filename), lines[i])

            elif 'File size' in lines[i]:
                lines[i] = re.sub(r": .+", ': ' + get_readable_file_size(float(filesize)), lines[i])

            elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
                duration = float(mediainfo_json['media']['track'][0]['Duration'])
                bitrate = get_readable_bitrate(float(filesize) * 8 / (duration * 1000))
                lines[i] = re.sub(r": .+", ': ' + bitrate, lines[i])

            elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                lines[i] = ''

        with open(f'{filename}.txt', 'w') as f:
            f.write('\n'.join(lines))

        with open(f"{filename}.txt", "r+") as file:
            content = file.read()
        output = await post_to_telegraph(False, "MissKaty MediaInfo", content)

        await reply_msg.edit(f"**File Name :** `{unquote(filename)}`\n\n**Mediainfo :** {output}",
                             disable_web_page_preview=True)
        os.remove(f"{filename}.txt")
        os.remove(filename)

    except:
        await reply_msg.delete()
        return await message.reply_text(f"Something went wrong while generating Mediainfo from the given url.",
                                        quote=True)


async def telegram_mediainfo(client, message):
    """
    Generates Mediainfo from a Telegram File.
    """

    message = message.reply_to_message

    if message.text:
        return await message.reply_text("Reply to a proper media file for generating Mediainfo.**", quote=True)

    elif message.media.value == 'video':
        media = message.video

    elif message.media.value == 'audio':
        media = message.audio

    elif message.media.value == 'document':
        media = message.document

    elif message.media.value == 'voice':
        media = message.voice

    else:
        return await message.reply_text("This type of media is not supported for generating Mediainfo.**", quote=True)

    filename = str(media.file_name)
    mime = media.mime_type
    size = media.file_size

    reply_msg = await message.reply_text("Generating Mediainfo, Please wait..", quote=True)

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

    mediainfo = subprocess.check_output(['mediainfo', filename]).decode("utf-8")
    mediainfo_json = json.loads(subprocess.check_output(['mediainfo', filename, '--Output=JSON']).decode("utf-8"))
    readable_size = get_readable_file_size(size)

    try:
        lines = mediainfo.splitlines()
        for i in range(len(lines)):
            if 'File size' in lines[i]:
                lines[i] = re.sub(r": .+", ': ' + readable_size, lines[i])

            elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:

                duration = float(mediainfo_json['media']['track'][0]['Duration'])
                bitrate_kbps = (size * 8) / (duration * 1000)
                bitrate = get_readable_bitrate(bitrate_kbps)

                lines[i] = re.sub(r": .+", ': ' + bitrate, lines[i])

            elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                lines[i] = ''

        remove_N(lines)
        with open(f'{filename}.txt', 'w') as f:
            f.write('\n'.join(lines))

        with open(f"{filename}.txt", "r+") as file:
            content = file.read()

        output = await post_to_telegraph(False, "MissKaty MediaInfo", content)

        await reply_msg.edit(f"**File Name :** `{filename}`\n\n**Mediainfo :** {output}", disable_web_page_preview=True)
        os.remove(f'{filename}.txt')
        os.remove(filename)

    except:
        await reply_msg.delete()
        await message.reply_text(f"Something went wrong while generating Mediainfo of replied Telegram file.", quote=True)




@app.on_message(filters.command("mediainfo2", COMMAND_HANDLER))
async def mediainfo(client, message):
    mediainfo_usage = f"**Generate mediainfo from Telegram files or direct download links. Reply to any telegram file or just pass the link after the command."
    
    if message.reply_to_message:
        return await telegram_mediainfo(client, message)

    elif len(message.command) < 2:
        return await message.reply_text(mediainfo_usage, quote=True)

    user_url = message.text.split(None, 1)[1].split(" ")[0]
    for (key, value) in SUPPORTED_URL_REGEX.items():
        if bool(re.search(FR"{key}", user_url)):
            if value == "ddl":
                return await ddl_mediainfo(client, message, url=user_url)
    await message.reply_text("This type of URL is not supported.", quote=True)