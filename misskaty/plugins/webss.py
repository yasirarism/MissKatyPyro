import base64
import os
from asyncio import gather
from io import BytesIO
from pyrogram import filters
from PIL import Image
from misskaty import app
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err

__MODULE__ = "WebSS"
__HELP__ = """
/webss [URL] - Take A Screenshot Of A Webpage.
"""


@app.on_message(filters.command(["webss"], COMMAND_HANDLER))
@capture_err
async def take_ss(_, message):
    if len(message.command) == 1:
        return await message.reply("Give A Url To Fetch Screenshot.")
    url = message.command[1]
    filename = f"imageToSave_{message.from_user.id}.png"
    m = await message.reply("Capturing screenshot...")
    try:
        photo = (await http.get(f"https://yasirapi.eu.org/webss?url={url}")).json()
        img = Image.open(BytesIO(base64.decodebytes(bytes(photo["result"], "utf-8"))))
        img.save(filename)
        m = await m.edit("Uploading...")
        await gather(*[message.reply_document(filename), message.reply_photo(filename)])
        await m.delete()
        os.remove(filename)
    except Exception as e:
        await m.edit(f"Failed To Take Screenshot. {str(e)}")
