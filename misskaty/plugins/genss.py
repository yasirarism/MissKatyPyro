"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import datetime
import os
import time
from asyncio import gather, sleep
from logging import getLogger

from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.message_utils import *
from misskaty.helper import gen_ik_buttons, get_duration, is_url, progress_for_pyrogram, screenshot_flink, take_ss
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

LOGGER = getLogger(__name__)

__MODULE__ = "MediaTool"
__HELP__ = """"
/genss [reply to video] - Generate Screenshot From Video. (Support TG Media and Direct URL)
/mediainfo [link/reply to TG Video] - Get Mediainfo From File.
"""


@app.on_message(filters.command(["genss"], COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def genss(c, m, strings):
    if not m.from_user:
        return
    replied = m.reply_to_message
    if len(m.command) == 2 and is_url(m.command[1]):
        snt = await kirimPesan(m, strings("wait_msg"), quote=True)

        duration = await get_duration(m.command[1])
        if isinstance(duration, str):
            return await editPesan(snt, strings("fail_open"))
        btns = gen_ik_buttons()
        await editPesan(snt, strings("choose_no_ss").format(td=datetime.timedelta(seconds=duration), dur=duration), reply_markup=InlineKeyboardMarkup(btns))
    elif replied and replied.media:
        vid = [replied.video, replied.document]
        media = next((v for v in vid if v is not None), None)
        if media is None:
            return await kirimPesan(m, strings("no_reply"), quote=True)
        process = await kirimPesan(m, strings("wait_dl"), quote=True)
        if media.file_size > 2097152000:
            return await editPesan(process, strings("limit_dl"))
        c_time = time.time()
        dl = await replied.download(
            file_name="/downloads/",
            progress=progress_for_pyrogram,
            progress_args=(strings("dl_progress"), process, c_time),
        )
        the_real_download_location = os.path.join("/downloads/", os.path.basename(dl))
        if the_real_download_location is not None:
            try:
                await editPesan(process, strings("sucess_dl_msg"))
                await sleep(2)
                images = await take_ss(the_real_download_location)
                await editPesan(process, strings("up_progress"))
                await c.send_chat_action(chat_id=m.chat.id, action=enums.ChatAction.UPLOAD_PHOTO)

                try:
                    await gather(
                        *[
                            m.reply_document(images, reply_to_message_id=m.id),
                            m.reply_photo(images, reply_to_message_id=m.id),
                        ]
                    )
                except FloodWait as e:
                    await sleep(e.value)
                    await gather(
                        *[
                            m.reply_document(images, reply_to_message_id=m.id),
                            m.reply_photo(images, reply_to_message_id=m.id),
                        ]
                    )
                await kirimPesan(
                    m,
                    strings("up_msg").format(namma=m.from_user.mention, id=m.from_user.id, bot_uname=c.me.username),
                    reply_to_message_id=m.id,
                )
                await process.delete()
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
            except Exception as exc:
                await kirimPesan(m, strings("err_ssgen").format(exc=exc))
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
    else:
        await kirimPesan(m, strings("no_reply"))


@app.on_callback_query(filters.regex(r"^scht"))
@ratelimiter
async def _(c, m):
    asyncio.create_task(screenshot_flink(c, m))
