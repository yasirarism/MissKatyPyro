# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import html
import random

from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError
from pyrogram import filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from misskaty import app
from misskaty.core import pyro_cooldown
from misskaty.helper import check_time_gap, fetch, post_to_telegraph, use_chat_lang
from misskaty.vars import GOOGLEAI_KEY, COMMAND_HANDLER, OPENAI_KEY, SUDO


__MODULE__ = "ChatBot"
__HELP__ = """
/ai - Generate text response from AI using Gemini AI By Google.
/ask - Generate text response from AI using OpenAI.
"""


@app.on_message(filters.command("ai", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@app.on_bot_business_message(filters.command("ai", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@use_chat_lang()
async def gemini_chatbot(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    if not GOOGLEAI_KEY:
        return await ctx.reply_msg("GOOGLEAI_KEY env is missing!!!")
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    try:
        data = {
            "query": ctx.text.split(maxsplit=1)[1],
        }
        response = await fetch.post(
            "https://yasirapi.eu.org/gemini", data=data
        )
        if not response.json().get("candidates"):
            await ctx.reply_msg("⚠️ Sorry, the prompt you sent maybe contains a forbidden word that is not permitted by AI.")
        else:
            await ctx.reply_msg(html.escape(response.json()["candidates"][0]["content"]["parts"][0]["text"]))
        await msg.delete()
    except Exception as e:
        await ctx.reply_msg(str(e))
        await msg.delete()


@app.on_message(filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@use_chat_lang()
async def openai_chatbot(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    if not OPENAI_KEY:
        return await ctx.reply_msg("OPENAI_KEY env is missing!!!")
    uid = ctx.from_user.id if ctx.from_user else ctx.sender_chat.id
    is_in_gap, _ = await check_time_gap(uid)
    if is_in_gap and (uid not in SUDO):
        return await ctx.reply_msg(strings("dont_spam"), del_in=5)
    ai = AsyncOpenAI(api_key=OPENAI_KEY, base_url="https://api.aimlapi.com")
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    num = 0
    answer = ""
    try:
        response = await ai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": pertanyaan}],
            temperature=0.7,
            stream=True,
        )
        async for chunk in response:
            if not chunk.choices[0].delta.content:
                continue
            num += 1
            answer += chunk.choices[0].delta.content
            if num == 30:
                await msg.edit_msg(html.escape(answer))
                await asyncio.sleep(1.5)
                num = 0
        await msg.edit_msg(html.escape(answer))
    except MessageTooLong:
        answerlink = await post_to_telegraph(
            False, "MissKaty ChatBot ", html.escape(f"<code>{answer}</code>")
        )
        await msg.edit_msg(
            strings("answers_too_long").format(answerlink=answerlink),
            disable_web_page_preview=True,
        )
    except APIConnectionError as e:
        await msg.edit_msg(f"The server could not be reached because {e.__cause__}")
    except RateLimitError as e:
        if "billing details" in str(e):
            return await msg.edit_msg("This openai key from this bot has expired, please give openai key donation for bot owner.")
        await msg.edit_msg("You're got rate limit, please try again later.")
    except APIStatusError as e:
        await msg.edit_msg(f"Another {e.status_code} status code was received with response {e.response}")
    except Exception as e:
        await msg.edit_msg(f"ERROR: {e}")
