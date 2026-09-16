# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import os
from asyncio import gather

from pyrogram.types import Message
from pySmartDL import SmartDL

from misskaty import app
from misskaty.core.decorator import new_task
from misskaty.helper.localization import use_chat_lang

__MODULE__ = "WebSS"
__HELP__ = """
/webss [URL] - Take A Screenshot Of A Webpage.
/webss [URL] -f - Capture full scrollable page.
"""


@app.on_cmd("webss")
@new_task
@use_chat_lang()
async def take_ss(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply(strings("no_url"), del_in=6)

    target_url = None
    is_full_page = "false"
    for arg in ctx.command[1:]:
        if arg.lower() in ("-f", "--full"):
            is_full_page = "true"
        elif not target_url and not arg.startswith("-"):
            target_url = arg

    if not target_url:
        return await ctx.reply(strings("no_url"), del_in=6)

    target_url = (
        target_url
        if target_url.startswith("http")
        else f"https://{target_url}"
    )
    user_id = ctx.from_user.id if ctx.from_user else ctx.chat.id
    os.makedirs("downloads", exist_ok=True)
    download_file_path = os.path.join("downloads/", f"webSS_{user_id}.jpg")
    msg = await ctx.reply(strings("wait_str"))
    try:
        api_url = (
            "https://webss.yasirweb.eu.org/api/screenshot"
            f"?resX=1280&resY=900&outFormat=jpg&waitTime=1000&isFullPage={is_full_page}&dismissModals=true&url={target_url}"
        )
        downloader = SmartDL(
            api_url, download_file_path, progress_bar=False, timeout=25, verify=False
        )
        downloader.start(blocking=True)
        await gather(
            *[
                ctx.reply_document(download_file_path),
                ctx.reply_photo(download_file_path, caption=strings("str_credit")),
            ]
        )
        await msg.delete_msg()
        if os.path.exists(download_file_path):
            os.remove(download_file_path)
    except Exception as e:
        await msg.edit(strings("ss_failed_str").format(err=str(e)))
