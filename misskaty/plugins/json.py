"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""

import os

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import app


# View Structure Telegram Message As JSON
@app.on_cmd("json")
async def jsonify(_, message: Message):
    the_real_message = None
    reply_to_id = None

    the_real_message = message.reply_to_message or message
    try:
        await message.reply_text(
            f"<code>{the_real_message}</code>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❌ Close",
                            callback_data=f"close#{message.from_user.id if message.from_user else 2024984460}",
                        )
                    ]
                ]
            ),
        )
    except Exception as e:
        with open("json.txt", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await message.reply_document(
            document="json.txt",
            caption=f"<code>{str(e)}</code>",
            disable_notification=True,
            reply_to_message_id=reply_to_id,
            thumb="assets/thumb.jpg",
        )
        os.remove("json.txt")
