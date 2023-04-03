import openai
from aiohttp import ClientSession
from pyrogram import filters
from pyrogram.errors import MessageTooLong

from misskaty import app
from misskaty.helper.localization import use_chat_lang
from misskaty.helper import http, post_to_telegraph, check_time_gap
from misskaty.core.message_utils import *
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.vars import COMMAND_HANDLER, OPENAI_API, SUDO

openai.api_key = OPENAI_API

@app.on_message(filters.command("ask", COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def chatbot(c, m, strings):
    if len(m.command) == 1:
        return await kirimPesan(m, strings("no_question").format(cmd=m.command[0]), quote=True)
    is_in_gap, sleep_time = await check_time_gap(m.from_user.id or m.sender_chat.id)
    if is_in_gap and (m.from_user.id or m.sender_chat.id not in SUDO):
        return await kirimPesan(m, strings("dont_spam"))
    openai.aiosession.set(ClientSession())
    pertanyaan = m.text.split(" ", maxsplit=1)[1]
    msg = await kirimPesan(m, strings("find_answers_str"), quote=True)
    num = 0
    answer = ""
    try:
        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "user", "content": pertanyaan}
            ],
            temperature=0.2,
            stream=True
        )
        async for chunk in response:
            if not chunk.choices[0].delta or chunk.choices[0].delta.get("role"):
                continue
            num += 1
            answer +=  chunk.choices[0].delta.content
            if num == 30:
                await editPesan(msg, answer)
                await asyncio.sleep(1)
                num = 0
        await openai.aiosession.get().close()
    except MessageTooLong:
        answerlink = await post_to_telegraph(False, "MissKaty ChatBot ", answer)
        await editPesan(msg, strings("answers_too_long").format(answerlink=answerlink), disable_web_page_preview=True)
    except Exception as err:
        await editPesan(msg, f"ERROR: {str(err)}")
