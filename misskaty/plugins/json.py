"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""

import os

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.vars import COMMAND_HANDLER


# View Structure Telegram Message As JSON
@app.on_message(filters.command(["json"], COMMAND_HANDLER))
async def jsonify(_, message):
    the_real_message = None
    reply_to_id = None

    the_real_message = message.reply_to_message or message
    try:
        await message.reply_text(
            f"<code>{the_real_message}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌ Close", callback_data=f"close#{msg.from_user.id}")]]),
        )
    except Exception as e:
        with open("json.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await message.reply_document(
            document="json.text",
            caption=f"<code>{str(e)}</code>",
            disable_notification=True,
            reply_to_message_id=reply_to_id,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌ Close", callback_data=f"close#{msg.from_user.id}")]]),
        )
        os.remove("json.text")
