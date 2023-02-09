import datetime
import os
import random
import shlex
import time
import traceback
import uuid
from pathlib import Path

from pyrogram import enums
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InputMediaPhoto)

from misskaty.core.message_utils import *


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return await process.communicate()

def get_random_start_at(seconds, dur=0):
    return random.randint(0, seconds-dur)

async def get_duration(input_file_link):
    ffmpeg_dur_cmd = f"ffprobe -v error -show_entries format=duration -of csv=p=0:s=x -select_streams v:0 {shlex.quote(input_file_link)}"
    #print(ffmpeg_dur_cmd)
    out, err = await run_subprocess(ffmpeg_dur_cmd)
    out = out.decode().strip()
    if not out:
        return err.decode()
    duration = round(float(out))
    if duration:
        return duration
    return 'No duration!'

def is_url(text):
    return text.startswith('http')

async def get_dimentions(input_file_link):
    ffprobe_cmd = f"ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x -select_streams v:0 {shlex.quote(input_file_link)}"
    output = await run_subprocess(ffprobe_cmd)
    try:
        width, height = [int(i.strip()) for i in output[0].decode().split('x')]
    except Exception as e:
        print(e)
        width, height = 1280, 534
    return width, height

async def screenshot_flink(c, m):
    
    chat_id = m.from_user.id
    # if c.CURRENT_PROCESSES.get(chat_id, 0) == 1:
    #     return await m.answer('You have reached the maximum parallel processes! Try again after one of them finishes.', show_alert=True)
    # if not c.CURRENT_PROCESSES.get(chat_id):
    #     c.CURRENT_PROCESSES[chat_id] = 0
    # c.CURRENT_PROCESSES[chat_id] += 1
    
    _, num_screenshots = m.data.split('+')
    num_screenshots = int(num_screenshots)
    media_msg = m.message.reply_to_message
    #print(media_msg)
    if media_msg.empty:
        await editPesan(m.message, 'Why did you delete the file 😠, Now i cannot help you 😒.')
        # c.CURRENT_PROCESSES[chat_id] -= 1
        return
    
    uid = str(uuid.uuid4())
    output_folder = Path("GenSS/").joinpath(uid)
    if not output_folder.exists():
        os.makedirs(output_folder)
    
    try:
        start_time = time.time()
        
        await editPesan(m.message, 'Give me some time bruh!! 😴')
        
        await editPesan(m.message, '😀 Taking Snaps!')
        file_link = m.message.reply_to_message.command[1]
        duration = await get_duration(file_link)
        if isinstance(duration, str):
            await editPesan(m.message, "Oops, What's that? Couldn't Open the file😟.")
            # c.CURRENT_PROCESSES[chat_id] -= 1
            return

        reduced_sec = duration - int(duration*2 / 100)
        print(f"Total seconds: {duration}, Reduced seconds: {reduced_sec}")
        screenshots = []
        ffmpeg_errors = ''
        
        screenshot_secs = [get_random_start_at(reduced_sec) for i in range(1, 1+num_screenshots)]
        width, height = await get_dimentions(file_link)
        
        for i, sec in enumerate(screenshot_secs):
            thumbnail_template = output_folder.joinpath(f'{i+1}.png')
            #print(sec)
            ffmpeg_cmd = f"mediaextract -hide_banner -ss {sec} -i {shlex.quote(file_link)} -vframes 1 '{thumbnail_template}'"
            output = await run_subprocess(ffmpeg_cmd)
            await editPesan(m.message, f'😀 `{i+1}` of `{num_screenshots}` generated!')
            if thumbnail_template.exists():
                screenshots.append(
                    InputMediaPhoto(
                        str(thumbnail_template),
                        caption=f"ScreenShot at {datetime.timedelta(seconds=sec)}"
                    )
                )
                continue
            ffmpeg_errors += output[1].decode() + '\n\n'
        
        #print(screenshots)
        if not screenshots:
            await editPesan(m.message, '😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥.')
            # c.CURRENT_PROCESSES[chat_id] -= 1
            return
        
        await editPesan(m.message, f'🤓 Its done , Now starting to upload!')
        await media_msg.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
        await media_msg.reply_media_group(screenshots, True)
        
        await editPesan(m.message, f'Completed in {datetime.timedelta(seconds=int(time.time()-start_time))}\n\nJoin @moviesonlydiscussion\n\n©️ @prgofficial')
        # c.CURRENT_PROCESSES[chat_id] -= 1
        
    except:
        aa = traceback.print_exc()
        await editPesan(m.message, '😟 Sorry! Screenshot generation failed, ERR: {aa} 😥.')
        # c.CURRENT_PROCESSES[chat_id] -= 1

def gen_ik_buttons():
    btns = []
    i_keyboard = []
    for i in range(2, 11):
        i_keyboard.append(
            InlineKeyboardButton(
                f"{i}",
                f"scht+{i}"
            )
        )
        if (i>2) and (i%2) == 1:
            btns.append(i_keyboard)
            i_keyboard = []
        if i==10:
            btns.append(i_keyboard)
    return btns