# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import asyncio
import html
import json
import random

from openai import APIConnectionError, APIStatusError, AsyncAzureOpenAI, RateLimitError
from pyrogram import filters
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
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    try:
        data = {"query": ctx.text.split(maxsplit=1)[1], "key": GOOGLEAI_KEY, "system_instructions": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi."}
        # Fetch from API beacuse my VPS is not supported
        response = await fetch.post("https://yasirapi.eu.org/gemini", data=data)
        if not response.json().get("candidates"):
            await ctx.reply_msg(
                "⚠️ Sorry, the prompt you sent maybe contains a forbidden word that is not permitted by AI."
            )
        else:
            await ctx.reply_msg(
                html.escape(
                    response.json()["candidates"][0]["content"]["parts"][0]["text"]
                )
                + "\n<b>Powered by:</b> <code>Gemini Flash 1.5</code>"
            )
        await msg.delete()
    except Exception as e:
        await ctx.reply_msg(str(e))
        await msg.delete()


@app.on_message(filters.command("ask", COMMAND_HANDLER) & pyro_cooldown.wait(10))
@use_chat_lang()
async def gpt4_chatbot(self, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            strings("no_question").format(cmd=ctx.command[0]), quote=True, del_in=5
        )
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    headers = {
        "accept": "text/event-stream",
        "accept-language": "en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-vqd-4": "4-198357088945086646073357605381970333191",
        "cookie": "dcm=3",
        "Referer": "https://duckduckgo.com/",
        "Referrer-Policy": "origin"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi."},
            {"role": "assistant", "content": "Halo! Saya MissKaty AI, kucing yang siap membantu kamu mencari informasi. Apa yang bisa saya bantu hari ini?"},
            {"role": "user", "content": pertanyaan}
        ]
    }
    response = await fetch.post("https://duckduckgo.com/duckchat/v1/chat", headers=headers, json=data)
    if response.status_code != 200:
        return await msg.edit_msg(f"ERROR: Status Code {response.status_code}")
    messages = []
    for line in response.text.splitlines():
        if line.startswith('data:'):
            try:
                json_data = json.loads(line[5:])
                if 'message' in json_data:
                    messages.append(json_data['message'])
            except json.JSONDecodeError:
                pass
    await msg.edit_msg(''.join(messages)+"\n\n<b>Powered by:</b> <code>GPT 4o Mini</code>")

# Temporary Disabled For Now Until I Have Key GPT
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
    ai = AsyncAzureOpenAI(api_key=OPENAI_KEY, azure_endpoint="https://yasirainew.openai.azure.com", api_version="2024-02-15-preview",)
    pertanyaan = ctx.input
    msg = await ctx.reply_msg(strings("find_answers_str"), quote=True)
    num = 0
    answer = ""
    try:
        response = await ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Kamu adalah AI dengan karakter mirip kucing bernama MissKaty AI yang diciptakan oleh Yasir untuk membantu manusia mencari informasi."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": pertanyaan
                        }
                    ]
                },
            ],
            temperature=0.7,
            stream=True,
        )
        async for chunk in response:
            if not chunk.choices:
                continue
            if not chunk.choices[0].delta.content:
                continue
            num += 1
            answer += chunk.choices[0].delta.content
            if num == 30:
                await msg.edit_msg(html.escape(answer))
                await asyncio.sleep(1.5)
                num = 0
        await msg.edit_msg(f"{html.escape(answer)}\n\n<b>Powered by:</b> <code>GPT 4o</code>")
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
            return await msg.edit_msg(
                "This openai key from this bot has expired, please give openai key donation for bot owner."
            )
        await msg.edit_msg("You're got rate limit, please try again later.")
    except APIStatusError as e:
        await msg.edit_msg(
            f"Another {e.status_code} status code was received with response {e.response}"
        )
    except Exception as e:
        await msg.edit_msg(f"ERROR: {e}")
