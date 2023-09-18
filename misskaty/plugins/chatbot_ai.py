# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import html
import random

import openai
from aiohttp import ClientSession
from pyrogram import filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from misskaty import app
from misskaty.core import pyro_cooldown
from misskaty.helper import check_time_gap, fetch, post_to_telegraph, use_chat_lang
from misskaty.vars import COMMAND_HANDLER, OPENAI_API, SUDO

openai.api_key = OPENAI_API


# This only for testing things, since maybe in future it will got blocked
@app.on_message(filters.command("bard", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@use_chat_lang()
async def bard_chatbot(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    try:
        req = await fetch.get(
            f"https://yasirapi.eu.org/bard?input={ctx.text.split(maxsplit=1)[1]}"
        )
        random_choice = random.choice(req.json().get("choices"))
        await msg.edit_msg(
            random_choice["content"][0]
            if req.json().get("content") != ""
            else "Failed getting data from Bard"
        )
    except Exception as e:
        await msg.edit_msg(str(e))


@app.on_message(filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@use_chat_lang()
async def openai_chatbot(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    uid = ctx.from_user.id if ctx.from_user else ctx.sender_chat.id
    is_in_gap, _ = await check_time_gap(uid)
    if is_in_gap and (uid not in SUDO):
        return await ctx.reply_msg(strings("dont_spam"), del_in=5)
    openai.aiosession.set(ClientSession())
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    num = 0
    answer = ""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": pertanyaan}],
            temperature=0.7,
            stream=True,
        )
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
    except MessageTooLong:
        answerlink = await post_to_telegraph(
            False, "MissKaty ChatBot ", html.escape(f"<code>{answer}</code>")
        )
        await msg.edit_msg(
            strings("answers_too_long").format(answerlink=answerlink),
            disable_web_page_preview=True,
        )
    except Exception as err:
        await msg.edit_msg(f"ERROR: {str(err)}")
    await openai.aiosession.get().close()
