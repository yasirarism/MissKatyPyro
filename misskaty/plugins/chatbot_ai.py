# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import html
import json
import random

from cachetools import TTLCache
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError
from pyrogram import filters, utils
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from misskaty import app
from misskaty.core import pyro_cooldown
from misskaty.helper import check_time_gap, fetch, post_to_telegraph, use_chat_lang
from misskaty.vars import COMMAND_HANDLER, GOOGLEAI_KEY, OPENAI_KEY, SUDO

__MODULE__ = "ChatBot"
__HELP__ = """
/ai - Generate text response from AI using Gemini AI By Google.
/ask - Generate text response from AI using OpenAI.
"""

duckai_conversations = TTLCache(maxsize=4000, ttl=24*60*60)
gemini_conversations = TTLCache(maxsize=4000, ttl=24*60*60)

async def get_openai_stream_response(is_stream, key, base_url, model, messages, bmsg, strings):
    ai = AsyncOpenAI(api_key=key, base_url=base_url)
    if is_stream:
        response = await ai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            stream=True,
        )
    else:
        response = await ai.chat.completions.create(
            extra_body={"model":model},
            model=model,
            messages=messages,
            temperature=0.7,
        )
    answer = ""
    num = 0
    try:
        if not is_stream:
            await bmsg.edit_msg(f"{response.choices[0].message.content}\n<b>Powered by:</b> <code>Gemini 1.5 Flash</code>")
            answer += response.choices[0].message.content
        else:
            async for chunk in response:
                if not chunk.choices or not chunk.choices[0].delta.content:
                    continue
                num += 1
                answer += chunk.choices[0].delta.content
                if num == 30:
                    await bmsg.edit_msg(html.escape(answer))
                    await asyncio.sleep(1.5)
                    num = 0
            await bmsg.edit_msg(f"{html.escape(answer)}\n\n<b>Powered by:</b> <code>GPT 4o Mini</code>")
    except MessageTooLong:
        answerlink = await post_to_telegraph(
            False, "MissKaty ChatBot ", html.escape(f"<code>{answer}</code>")
        )
        await bmsg.edit_msg(
            strings("answers_too_long").format(answerlink=answerlink),
            disable_web_page_preview=True,
        )
    except APIConnectionError as e:
        await bmsg.edit_msg(f"The server could not be reached because {e.__cause__}")
        return None
    except RateLimitError as e:
        if "billing details" in str(e):
            return await bmsg.edit_msg(
                "This openai key from this bot has expired, please give openai key donation for bot owner."
            )
        await bmsg.edit_msg("You're got rate limit, please try again later.")
        return None
    except APIStatusError as e:
        await bmsg.edit_msg(
            f"Another {e.status_code} status code was received with response {e.response}"
        )
        return None
    except Exception as e:
        await bmsg.edit_msg(f"ERROR: {e}")
        return None
    return answer


@app.on_message(filters.command("ai", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@app.on_bot_business_message(
    filters.command("ai", COMMAND_HANDLER) & pyro_cooldown.wait(10)
)
@use_chat_lang()
async def gemini_chatbot(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    if not GOOGLEAI_KEY:
        return await ctx.reply_msg("GOOGLEAI_KEY env is missing!!!")
    uid = ctx.from_user.id if ctx.from_user else ctx.sender_chat.id
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    if uid not in gemini_conversations:
        gemini_conversations[uid] = [{"role": "system", "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi."}, {"role": "user", "content": ctx.input}]
    else:
        gemini_conversations[uid].append({"role": "user", "content": ctx.input})
    ai_response = await get_openai_stream_response(False, GOOGLEAI_KEY, "https://gemini.yasirapi.eu.org/v1", "gemini-1.5-flash", gemini_conversations[uid], msg, strings)
    if not ai_response:
        gemini_conversations[uid].pop()
        if len(gemini_conversations[uid]) == 1:
            gemini_conversations.pop(uid)
        return
    gemini_conversations[uid].append({"role": "assistant", "content": ai_response})

@app.on_message(filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@use_chat_lang()
async def openai_chatbot(self, ctx: Message, strings):
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
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    if uid not in duckai_conversations:
        duckai_conversations[uid] = [{"role": "system", "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi."}, {"role": "user", "content": pertanyaan}]
    else:
        duckai_conversations[uid].append({"role": "user", "content": pertanyaan})
    ai_response = await get_openai_stream_response(True, OPENAI_KEY, "https://duckai.yasirapi.eu.org/v1", "gpt-4o-mini", duckai_conversations[uid], msg, strings)
    if not ai_response:
        duckai_conversations[uid].pop()
        if len(duckai_conversations[uid]) == 1:
            duckai_conversations.pop(uid)
        return
    duckai_conversations[uid].append({"role": "assistant", "content": ai_response})
