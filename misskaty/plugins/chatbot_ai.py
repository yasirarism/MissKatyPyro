from pyrogram import filters
from pyrogram.errors import MessageTooLong

from misskaty import app
from misskaty.helper.localization import use_chat_lang
from misskaty.helper import http, post_to_telegraph
from misskaty.core.message_utils import *
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.vars import COMMAND_HANDLER, OPENAI_API


@app.on_message(filters.command("ask", COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def chatbot(c, m, strings):
    if len(m.command) == 1:
        return await kirimPesan(m, strings("no_question").format(cmd=m.command[0]), quote=True)
    pertanyaan = m.text.split(" ", maxsplit=1)[1]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API}",
    }

    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": pertanyaan,
            },
        ],
    }
    msg = await kirimPesan(m, strings("find_answers_str"), quote=True)
    try:
        response = (await http.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)).json()
        if err := response.get("error"):
            return await editPesan(msg, err["message"])
        answer = response["choices"][0]["message"]["content"]
        await editPesan(msg, answer)
    except MessageTooLong:
        answerlink = await post_to_telegraph(False, "MissKaty ChatBot ", answer)
        await editPesan(msg, strings("answers_too_long").format(answerlink=answerlink), disable_web_page_preview=True)
    except Exception as err:
        await editPesan(msg, f"ERROR: {str(err)}")
