import os
from asyncio import gather

from pyrogram import filters

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "WebSS"
__HELP__ = """
/webss [URL] - Take A Screenshot Of A Webpage.
"""


@app.on_message(filters.command(["webss"], COMMAND_HANDLER))
@capture_err
@ratelimiter
async def take_ss(_, m):
    if len(m.command) == 1:
        return await kirimPesan(m, "Give A Url To Fetch Screenshot.")
    url = m.command[1] if m.command[1].startswith("http") else f"https://{m.command[1]}"
    filename = f"webSS_{m.from_user.id}.png"
    msg = await m.reply("Capturing screenshot...")
    try:
        url = f"https://webss.yasirapi.eu.org/api?url={url}&width=1280&height=720"
        await gather(*[m.reply_document(url, file_name=filename), m.reply_photo(url)])
        await hapusPesan(msg)
    except Exception as e:
        await editPesan(msg, f"Failed To Take Screenshot. {str(e)}")
