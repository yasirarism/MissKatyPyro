import asyncio
import os
import time
from pyrogram.types import InputMediaPhoto
from bot.plugins.dev import shell_exec
from pyrogram.errors import FloodWait


def hhmmss(seconds):
    x = time.strftime("%H:%M:%S", time.gmtime(seconds))
    return x


async def take_ss(video_file):
    out_put_file_name = f"genss{str(time.time())}.png"
    file_genertor_command = ["vcsi", video_file, "-t", "-w", "850", "-g", "3x4", "--metadata-font", "Calistoga-Regular.ttf", "--timestamp-font", "Calistoga-Regular.ttf", "--quality", "100", "--end-delay-percent", "20", "-o", out_put_file_name]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


async def ssgen_link(video, output_directory, ttl):
    out_put_file_name = output_directory + "/" + str(time.time()) + ".png"
    cmd = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video,
        "-vframes",
        "1",
        "-f",
        "image2",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    if os.path.isfile(out_put_file_name):
        return out_put_file_name
    else:
        return None


async def genss_link(msg, video_link, output_directory, min_duration, no_of_photos):
    metadata = (await shell_exec(f"ffprobe -i {video_link} -show_entries format=duration -v quiet -of csv='p=0'"))[0]
    duration = round(float(metadata))
    if duration > min_duration:
        images = []
        ttl_step = duration // no_of_photos
        current_ttl = ttl_step
        for looper in range(0, no_of_photos):
            ss_img = await ssgen_link(video_link, output_directory, current_ttl)
            images.append(InputMediaPhoto(media=ss_img, caption=f"Screenshot at {hhmmss(current_ttl)}"))
            try:
                await msg.edit(f"📸 <b>Take Screenshoot:</b>\n<code>{looper+1} of {no_of_photos} screenshot generated..</code>")
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await msg.edit(f"📸 <b>Take Screenshoot:</b>\n<code>{looper+1} of {no_of_photos} screenshot generated..</code>")
            current_ttl = current_ttl + ttl_step
            await asyncio.sleep(2)
        return images
    else:
        return None
