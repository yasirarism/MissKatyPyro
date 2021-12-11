from info import COMMAND_HANDLER
import requests
import json
import os
from pyrogram import filters
from bot import app

@app.on_message(filters.command(["ocr","ocr@MissKatyRoBot"], COMMAND_HANDLER))
async def ocr(_, message):
  reply = message.reply_to_message
  if not reply and not reply.photo:
    return await message.reply_text("Balas pesan foto dengan command /ocr")
  msg = await message.reply("Reading image...")
  try:
    file_path = await reply.download()
    response = upload_file(image)
    url = f"https://telegra.ph{response[0]}"
    req = requests.get(f"https://script.google.com/macros/s/AKfycbwmaiH74HX_pL-iNzw8qUsHoDMtBIBLogclgLD6cNLpPM6piGg/exec?url={url}").json()
    await msg.edit(re)
  except Exception as e:
    await msg.edit(str(e))
