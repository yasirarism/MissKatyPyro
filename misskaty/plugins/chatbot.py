from pyrogram import filters
from pyrogram.errors import MessageNotModified

from misskaty import app
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER, OPENAI_API


@app.on_message(filters.command("ask", COMMAND_HANDLER))
async def chatbot(c, m):
    if len(m.command) == 1:
        return await m.reply(f"Gunakan perintah <code>/{m.command[0]} [pertanyaan]</code> untuk menanyakan pertanyaan menggunakan AI.")
    pertanyaan = m.text.split(" ", maxsplit=1)[1]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API}",
    }

    json_data = {
        "model": "text-davinci-003",
        "prompt": pertanyaan,
        "max_tokens": 200,
        "temperature": 0,
    }
    msg = await m.reply("Wait a moment looking for your answer..")
    try:
        response = (await http.post("https://api.openai.com/v1/completions", headers=headers, json=json_data)).json()
        await msg.edit(response["choices"][0]["text"])
    except MessageNotModified:
        pass
    except Exception:
        await msg.edit("Yahh, sorry i can't get your answer.")
