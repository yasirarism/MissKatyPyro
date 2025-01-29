# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import html
import privatebinapi

from cachetools import TTLCache
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError
from pyrogram import filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from misskaty import app
from misskaty.core import pyro_cooldown
from misskaty.helper import check_time_gap, post_to_telegraph, use_chat_lang
from misskaty.vars import COMMAND_HANDLER, GOOGLEAI_KEY, OPENAI_KEY, OWNER_ID, SUDO

__MODULE__ = "ChatBot"
__HELP__ = """
/ai - Generate text response from AI using Gemini AI By Google.
/ask - Generate text response from AI using OpenAI.
"""

gptai_conversations = TTLCache(maxsize=4000, ttl=24*60*60)
gemini_conversations = TTLCache(maxsize=4000, ttl=24*60*60)

async def get_openai_stream_response(is_stream, key, base_url, model, messages, bmsg, strings):
    ai = AsyncOpenAI(api_key=key, base_url=base_url)
    answer = ""
    num = 0
    try:
        response = await ai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            stream=is_stream,
        )
        if not is_stream:
            answer += response.choices[0].message.content
            if len(answer) > 4000:
                answerlink = await privatebinapi.send_async("https://bin.yasirweb.eu.org", text=answer, expiration="1week", formatting="markdown")
                await bmsg.edit_msg(
                    strings("answers_too_long").format(answerlink=answerlink.get("full_url")),
                    disable_web_page_preview=True,
                )
            else:
                await bmsg.edit_msg(f"{html.escape(answer)}\n<b>Powered by:</b> <code>Gemini 1.5 Flash</code>")
        else:
            async for chunk in response:
                if not chunk.choices or not chunk.choices[0].delta.content:
                    continue
                num += 1
                answer += chunk.choices[0].delta.content
                if num == 30 and len(answer) < 4000:
                    await bmsg.edit_msg(html.escape(answer))
                    await asyncio.sleep(1.5)
                    num = 0
            if len(answer) > 4000:
                answerlink = await privatebinapi.send_async("https://bin.yasirweb.eu.org", text=answer, expiration="1week", formatting="markdown")
                await bmsg.edit_msg(
                    strings("answers_too_long").format(answerlink=answerlink.get("full_url")),
                    disable_web_page_preview=True,
                )
            else:
                await bmsg.edit_msg(f"{html.escape(answer)}\n\n<b>Powered by:</b> <code>GPT 4o</code>")
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
        gemini_conversations[uid] = [{"role": "system", "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi dan gunakan bahasa sesuai yang saya katakan."}, {"role": "user", "content": ctx.input}]
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
@app.on_bot_business_message(
    filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10)
)
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
    if is_in_gap and (uid != OWNER_ID or uid not in SUDO):
        return await ctx.reply_msg(strings("dont_spam"), del_in=5)
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    if uid not in gptai_conversations:
        gptai_conversations[uid] = [{"role": "system", "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi dan gunakan bahasa sesuai yang saya katakan."}, {"role": "user", "content": pertanyaan}]
    else:
        gptai_conversations[uid].append({"role": "user", "content": pertanyaan})
    ai_response = await get_openai_stream_response(True, OPENAI_KEY, "https://models.inference.ai.azure.com", "gpt-4o-mini", gptai_conversations[uid], msg, strings)
    if not ai_response:
        gptai_conversations[uid].pop()
        if len(gptai_conversations[uid]) == 1:
            gptai_conversations.pop(uid)
        return
    gptai_conversations[uid].append({"role": "assistant", "content": ai_response})
