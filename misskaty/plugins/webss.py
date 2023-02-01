import base64
import os
from asyncio import gather
from io import BytesIO

from PIL import Image
from pyrogram import filters

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "WebSS"
__HELP__ = """
/webss [URL] - Take A Screenshot Of A Webpage.
"""


@app.on_message(filters.command(["webss"], COMMAND_HANDLER))
@capture_err
async def take_ss(_, m):
    if len(m.command) == 1:
        return await kirimPesan(m, "Give A Url To Fetch Screenshot.")
    url = m.command[1] if m.command[1].startswith("http") else f"https://{m.command[1]}"
    filename = f"webSS_{m.from_user.id}.jpg"
    msg = await m.reply("Capturing screenshot...")
    try:
        photo = (await http.get(f"https://yasirapi.eu.org/webss?url={url}")).json()
        img = Image.open(BytesIO(base64.decodebytes(bytes(photo["result"], "utf-8"))))
        img.save(filename)
        await editPesan(msg, "Uploading...")
        await gather(*[m.reply_document(filename), m.reply_photo(filename)])
        await hapusPesan(m)
        os.remove(filename)
    except Exception as e:
        await editPesan(msg, f"Failed To Take Screenshot. {str(e)}")
