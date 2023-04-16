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
from asyncio import create_task, gather, sleep
from logging import getLogger

from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import (
    gen_ik_buttons,
    get_duration,
    is_url,
    progress_for_pyrogram,
    screenshot_flink,
    take_ss,
)
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
async def genss(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return
    replied = ctx.reply_to_message
    if len(ctx.command) == 2 and is_url(ctx.command[1]):
        snt = await ctx.reply_msg(strings("wait_msg"), quote=True)

        duration = await get_duration(ctx.command[1])
        if isinstance(duration, str):
            return await snt.edit_msg(strings("fail_open"))
        btns = gen_ik_buttons()
        await snt.edit_msg(
            strings("choose_no_ss").format(
                td=datetime.timedelta(seconds=duration), dur=duration
            ),
            reply_markup=InlineKeyboardMarkup(btns),
        )
    elif replied and replied.media:
        vid = [replied.video, replied.document]
        media = next((v for v in vid if v is not None), None)
        if media is None:
            return await ctx.reply_msg(strings("no_reply"), quote=True)
        process = await ctx.reply_msg(strings("wait_dl"), quote=True)
        if media.file_size > 2097152000:
            return await process.edit_msg(strings("limit_dl"))
        c_time = time.time()
        dl = await replied.download(
            file_name="/downloads/",
            progress=progress_for_pyrogram,
            progress_args=(strings("dl_progress"), process, c_time),
        )
        the_real_download_location = os.path.join("/downloads/", os.path.basename(dl))
        if the_real_download_location is not None:
            try:
                await process.edit_msg(
                    strings("success_dl_msg").format(path=the_real_download_location)
                )
                await sleep(2)
                images = await take_ss(the_real_download_location)
                await process.edit_msg(strings("up_progress"))
                await self.send_chat_action(
                    chat_id=ctx.chat.id, action=enums.ChatAction.UPLOAD_PHOTO
                )

                try:
                    await gather(
                        *[
                            ctx.reply_document(images, reply_to_message_id=ctx.id),
                            ctx.reply_photo(images, reply_to_message_id=ctx.id),
                        ]
                    )
                except FloodWait as e:
                    await sleep(e.value)
                    await gather(
                        *[
                            ctx.reply_document(images, reply_to_message_id=ctx.id),
                            ctx.reply_photo(images, reply_to_message_id=ctx.id),
                        ]
                    )
                await ctx.reply_msg(
                    strings("up_msg").format(
                        namma=ctx.from_user.mention,
                        id=ctx.from_user.id,
                        bot_uname=self.me.username,
                    ),
                    reply_to_message_id=ctx.id,
                )
                await process.delete()
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
            except Exception as exc:
                await ctx.reply_msg(strings("err_ssgen").format(exc=exc))
                try:
                    os.remove(images)
                    os.remove(the_real_download_location)
                except:
                    pass
    else:
        await ctx.reply_msg(strings("no_reply"), del_in=6)


@app.on_callback_query(filters.regex(r"^scht"))
@ratelimiter
async def genss_cb(self: Client, cb: CallbackQuery):
    create_task(screenshot_flink(self, cb))
