import asyncio
import os
import time
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InputMediaPhoto
from bot.plugins.dev import shell_exec

def hhmmss(seconds):
    x = time.strftime('%H:%M:%S',time.gmtime(seconds))
    return x

async def take_ss(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
    
async def ssgen_link(video, output_directory, ttl):
    out_put_file_name = output_directory + \
        "/" + str(time.time()) + ".jpg"
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
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
        
    stdout, stderr = await process.communicate()
    x = stderr.decode().strip()
    y = stdout.decode().strip()
    if os.path.isfile(out_put_file_name):
        return out_put_file_name
    else:
        return None
    
async def genss_link(
    msg,
    video_link,
    output_directory,
    min_duration,
    no_of_photos
):
    metadata = await shell_exec(f"ffprobe -i {video_link} -show_entries format=duration -v quiet -of csv='p=0'")
    duration = round(metadata)
    if duration > min_duration:
        images = []
        ttl_step = duration // no_of_photos
        current_ttl = ttl_step
        for looper in range(0, no_of_photos):
            ss_img = await ssgen_link(video_link, output_directory, current_ttl)
            images.append(InputMediaPhoto(media=ss_img, caption=f'Screenshot at {hhmmss(current_ttl)}'))
            await msg.edit(f"📸 <b>Take Screenshoot:</b>\n<code>{looper+1} of {no_of_photos} screenshot generated..</code>")
            current_ttl = current_ttl + ttl_step
            await asyncio.sleep(1)
        return images
    else:
        return None

async def generate_screen_shots(
    msg,
    video_file,
    output_directory,
    min_duration,
    no_of_photos
):
    metadata = extractMetadata(createParser(video_file))
    duration = 0
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
    if duration > min_duration:
        images = []
        ttl_step = duration // no_of_photos
        current_ttl = ttl_step
        for looper in range(0, no_of_photos):
            ss_img = await take_ss(video_file, output_directory, current_ttl)
            images.append(InputMediaPhoto(media=ss_img, caption=f'Screenshot at {hhmmss(current_ttl)}'))
            await msg.edit(f"📸 <b>Take Screenshoot:</b>\n<code>{looper+1} of {no_of_photos} screenshot generated..</code>")
            current_ttl = current_ttl + ttl_step
            await asyncio.sleep(1)
        return images
    else:
        return None
