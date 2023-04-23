import asyncio
import html

import openai
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import check_time_gap, post_to_telegraph
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER, OPENAI_API, SUDO

openai.api_key = OPENAI_API


@app.on_message(filters.command("ask", COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def chatbot(self: Client, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5)
    is_in_gap, sleep_time = await check_time_gap(ctx.from_user.id or ctx.sender_chat.id)
    if is_in_gap and (ctx.from_user.id or ctx.sender_chat.id not in SUDO):
        return await ctx.reply_msg(strings("dont_spam"), del_in=5)
    openai.aiosession.set(ClientSession())
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    num = 0
    answer = ""
    try:
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=[{"role": "user", "content": pertanyaan}], temperature=0.2, stream=True)
        async for chunk in response:
            if not chunk.choices[0].delta or chunk.choices[0].delta.get("role"):
                continue
            num += 1
            answer += chunk.choices[0].delta.content
            if num == 30:
                await msg.edit_msg(answer)
                await asyncio.sleep(1.5)
                num = 0
        await msg.edit_msg(answer)
        await openai.aiosession.get().close()
    except MessageTooLong:
        answerlink = await post_to_telegraph(False, "MissKaty ChatBot ", html.escape(answer))
        await msg.edit_msg(strings("answers_too_long").format(answerlink=answerlink), disable_web_page_preview=True)
    except Exception as err:
        await msg.edit_msg(f"ERROR: {str(err)}")
