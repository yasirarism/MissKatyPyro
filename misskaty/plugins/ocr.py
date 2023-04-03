"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""

import os

from pyrogram import filters
from telegraph.aio import Telegraph

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "OCR"
__HELP__ = f"/ocr [reply to photo] - Read Text From Image"


@app.on_message(filters.command(["ocr"], COMMAND_HANDLER))
@capture_err
@ratelimiter
@use_chat_lang()
async def ocr(_, m, strings):
    reply = m.reply_to_message
    if not reply or not reply.photo or (reply.document and not reply.document.mime_type.startswith("image")) and not reply.sticker:
        return await kirimPesan(m, strings("no_photo").format(cmd=m.command[0]), quote=True)
    msg = await kirimPesan(m, strings("read_ocr"), quote=True)
    try:
        file_path = await reply.download()
        if reply.sticker:
            file_path = await reply.download(f"ocr_{m.from_user.id}.jpg")
        response = await Telegraph().upload_file(file_path)
        url = f"https://telegra.ph{response[0]['src']}"
        req = (
            await http.get(
                f"https://script.google.com/macros/s/AKfycbwURISN0wjazeJTMHTPAtxkrZTWTpsWIef5kxqVGoXqnrzdLdIQIfLO7jsR5OQ5GO16/exec?url={url}",
                follow_redirects=True,
            )
        ).json()
        await editPesan(msg, strings("result_ocr").format(result=req["text"]))
        os.remove(file_path)
    except Exception as e:
        await editPesan(msg, str(e))
        os.remove(file_path)
