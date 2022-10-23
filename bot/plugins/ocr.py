from info import COMMAND_HANDLER
import requests
import os
from telegraph import upload_file
from pyrogram import filters
from bot import app
from bot.core.decorator.errors import capture_err

__MODULE__ = "OCR"
__HELP__ = "/ocr [reply to photo] - Read Text From Image"


@app.on_message(filters.command(["ocr"], COMMAND_HANDLER))
@capture_err
async def ocr(_, message):
    reply = message.reply_to_message
    if not reply or not reply.photo and not reply.sticker:
        return await message.reply_text(f"Reply photo with /{message.command[0]} command")
    msg = await message.reply("Reading image...")
    try:
        file_path = await reply.download()
        if reply.sticker:
            file_path = await reply.download(f"ocr{message.from_user.id}.jpg")
        response = upload_file(file_path)
        url = f"https://telegra.ph{response[0]}"
        req = requests.get(f"https://script.google.com/macros/s/AKfycbwmaiH74HX_pL-iNzw8qUsHoDMtBIBLogclgLD6cNLpPM6piGg/exec?url={url}").json()
        await msg.edit(f"Hasil OCR:\n<code>{req['text']}</code>")
        os.remove(file_path)
    except Exception as e:
        await msg.edit(str(e))
        os.remove(file_path)
