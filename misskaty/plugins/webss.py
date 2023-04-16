from asyncio import gather

from pyrogram import filters, Client
from pyrogram.types import Message

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "WebSS"
__HELP__ = """
/webss [URL] - Take A Screenshot Of A Webpage.
"""


@app.on_message(filters.command(["webss"], COMMAND_HANDLER))
@capture_err
@ratelimiter
@use_chat_lang()
async def take_ss(self: Client, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(strings("no_url"), del_in=6)
    url = ctx.command[1] if ctx.command[1].startswith("http") else f"https://{ctx.command[1]}"
    filename = f"webSS_{ctx.from_user.id}.png"
    msg = await ctx.reply_msg(strings("wait_str"))
    try:
        url = f"https://webss.yasirapi.eu.org/api?url={url}&width=1280&height=720"
        await gather(*[ctx.reply_document(url, file_name=filename), ctx.reply_photo(url)])
        await msg.delete_msg()
    except Exception as e:
        await msg.edit_msg(strings("ss_failed_str").format(err=str(e)))
