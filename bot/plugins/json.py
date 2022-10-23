import os
from pyrogram import filters
from bot import app
from info import COMMAND_HANDLER


@app.on_message(filters.command(["json"], COMMAND_HANDLER))
async def jsonify(_, message):
    the_real_message = None
    reply_to_id = None

    the_real_message = message.reply_to_message or message
    try:
        await message.reply_text(f"<code>{the_real_message}</code>")
    except Exception as e:
        with open("json.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await message.reply_document(document="json.text", caption=str(e), disable_notification=True, reply_to_message_id=reply_to_id)
        os.remove("json.text")
