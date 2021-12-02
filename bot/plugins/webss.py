import os
import asyncio
from pyrogram import filters
from bot import app
from info import COMMAND_HANDLER

@app.on_message(filters.command(["webss","webss@MissKatyRoBot"], COMMAND_HANDLER))
async def take_ss(_, message):
    try:
        if len(message.command) != 2 or message.reply_to_message:
            return await message.reply_text("Gunakan format /webss [URL] untuk mengambil screenshot web")
        link = message.text.split(None, 1)[1]
        download_file_path = os.path.join("/downloads", f"webss_{message.from_user.id}.jpg")
        url = f"http://public-restapi.herokuapp.com/api/web-page-screenshot?url={link}&width=1280&height=720"
        m = await message.reply_text("**Mengambil Screenshot..**")
        await asyncio.sleep(1)
        try:
            await m.edit("**Mengupload gambar..**")
            await app.send_chat_action(message.chat.id, "upload_photo")
            await message.reply_photo(
                photo=url,
                caption=f"<code>webss_{message.from_user.id}</code>",
                quote=True
            )
        except TypeError:
            return await m.edit("No Such Website.")
        await m.delete()
    except Exception as e:
        await message.reply_text(str(e))
