from info import COMMAND_HANDLER
import requests
import json
import os
from telegraph import upload_file
from pyrogram import filters
from bot import app

@app.on_message(filters.command(["ocr","ocr@MissKatyRoBot"], COMMAND_HANDLER))
async def ocr(_, message):
  reply = message.reply_to_message
  if not reply or not reply.photo and not reply.sticker:
    return await message.reply_text("Balas pesan foto dengan command /ocr")
  msg = await message.reply("Reading image...")
  try:
    img = await reply.download()
    if reply.sticker:
      img = await reply.download(f"ocr{message.from_user.id}.jpg")
    response = upload_file(img)
    url = f"https://telegra.ph{response[0]}"
    req = requests.get(f"https://script.google.com/macros/s/AKfycbwmaiH74HX_pL-iNzw8qUsHoDMtBIBLogclgLD6cNLpPM6piGg/exec?url={url}").json()
    await msg.edit(f"Hasil OCR:\n<code>{req['text']}</code>")
    os.remove(file_path)
  except Exception as e:
    await msg.edit(str(e))
    os.remove(file_path)
