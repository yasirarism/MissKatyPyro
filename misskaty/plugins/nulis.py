# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import os

from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters

from misskaty import app
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "nulis"
__HELP__ = """
Command: <code>/nulis</code> [reply to msg or after cmd]
Desc: For those of you who are lazy to write.
"""


def text_set(text):
    lines = []
    if len(text) <= 55:
        lines.append(text)
    else:
        all_lines = text.split("\n")
        for line in all_lines:
            if len(line) <= 55:
                lines.append(line)
            else:
                k = len(line) // 55
                lines.extend(line[((z - 1) * 55) : (z * 55)] for z in range(1, k + 2))
    return lines[:25]


@app.on_message(filters.command(["nulis"], COMMAND_HANDLER))
async def handwrite(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        txt = message.reply_to_message.text
    elif len(message.command) > 1:
        txt = message.text.split(None, 1)[1]
    else:
        return await message.reply(
            "Please reply to message or write after command to use Nulis CMD."
        )
    nan = await message.reply_msg("Processing...")
    try:
        img = Image.open("assets/kertas.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("assets/assfont.ttf", 30)
        x, y = 150, 140
        lines = text_set(txt)
        line_height = font.getbbox("hg")[3]
        for line in lines:
            draw.text((x, y), line, fill=(1, 22, 55), font=font)
            y = y + line_height - 5
        file = f"nulis_{message.from_user.id}.jpg"
        img.save(file)
        if os.path.exists(file):
            await message.reply_photo(
                photo=file, caption=f"<b>Written By :</b> {client.me.mention}"
            )
            os.remove(file)
            await nan.delete()
    except Exception as e:
        return await message.reply(e)
