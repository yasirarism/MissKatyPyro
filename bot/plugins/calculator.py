from bot import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import COMMAND_HANDLER

CALCULATE_TEXT = "Calculator Inline By MissKaty"


@app.on_message(filters.command(["calc"], COMMAND_HANDLER))
async def calculate(_, message):
    CALCULATE_BUTTONS = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "DEL", callback_data=f"cal_{message.from_user.id}_DEL"),
            InlineKeyboardButton(
                "AC", callback_data=f"cal_{message.from_user.id}_AC"),
            InlineKeyboardButton(
                "(", callback_data=f"cal_{message.from_user.id}_("),
            InlineKeyboardButton(")",
                                 callback_data=f"cal_{message.from_user.id}_)")
        ],
        [
            InlineKeyboardButton(
                "7", callback_data=f"cal_{message.from_user.id}_7"),
            InlineKeyboardButton(
                "8", callback_data=f"cal_{message.from_user.id}_8"),
            InlineKeyboardButton(
                "9", callback_data=f"cal_{message.from_user.id}_9"),
            InlineKeyboardButton("÷",
                                 callback_data=f"cal_{message.from_user.id}_/")
        ],
        [
            InlineKeyboardButton(
                "4", callback_data=f"cal_{message.from_user.id}_4"),
            InlineKeyboardButton(
                "5", callback_data=f"cal_{message.from_user.id}_5"),
            InlineKeyboardButton(
                "6", callback_data=f"cal_{message.from_user.id}_6"),
            InlineKeyboardButton("×",
                                 callback_data=f"cal_{message.from_user.id}_*")
        ],
        [
            InlineKeyboardButton(
                "1", callback_data=f"cal_{message.from_user.id}_1"),
            InlineKeyboardButton(
                "2", callback_data=f"cal_{message.from_user.id}_2"),
            InlineKeyboardButton(
                "3", callback_data=f"cal_{message.from_user.id}_3"),
            InlineKeyboardButton(
                "-", callback_data=f"cal_{message.from_user.id}_-"),
        ],
        [
            InlineKeyboardButton(
                ".", callback_data=f"cal_{message.from_user.id}_."),
            InlineKeyboardButton(
                "0", callback_data=f"cal_{message.from_user.id}_0"),
            InlineKeyboardButton(
                "=", callback_data=f"cal_{message.from_user.id}_="),
            InlineKeyboardButton(
                "+", callback_data=f"cal_{message.from_user.id}_+"),
        ]
    ])
    await message.reply_text(text=CALCULATE_TEXT,
                             reply_markup=CALCULATE_BUTTONS,
                             disable_web_page_preview=True,
                             quote=True)


@app.on_callback_query(filters.regex("^cal"))
async def cb_data(_, query):
    i, user, cmd = query.data.split('_')
    if user == f"{query.from_user.id}":
        CALCULATE_BUTTONS = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "DEL", callback_data=f"cal_{query.from_user.id}_DEL"),
                InlineKeyboardButton(
                    "AC", callback_data=f"cal_{query.from_user.id}_AC"),
                InlineKeyboardButton(
                    "(", callback_data=f"cal_{query.from_user.id}_("),
                InlineKeyboardButton(
                    ")", callback_data=f"cal_{query.from_user.id}_)")
            ],
             [
                 InlineKeyboardButton(
                     "7", callback_data=f"cal_{query.from_user.id}_7"),
                 InlineKeyboardButton(
                     "8", callback_data=f"cal_{query.from_user.id}_8"),
                 InlineKeyboardButton(
                     "9", callback_data=f"cal_{query.from_user.id}_9"),
                 InlineKeyboardButton(
                     "÷", callback_data=f"cal_{query.from_user.id}_/")
             ],
             [
                 InlineKeyboardButton(
                     "4", callback_data=f"cal_{query.from_user.id}_4"),
                 InlineKeyboardButton(
                     "5", callback_data=f"cal_{query.from_user.id}_5"),
                 InlineKeyboardButton(
                     "6", callback_data=f"cal_{query.from_user.id}_6"),
                 InlineKeyboardButton(
                     "×", callback_data=f"cal_{query.from_user.id}_*")
             ],
             [
                 InlineKeyboardButton(
                     "1", callback_data=f"cal_{query.from_user.id}_1"),
                 InlineKeyboardButton(
                     "2", callback_data=f"cal_{query.from_user.id}_2"),
                 InlineKeyboardButton(
                     "3", callback_data=f"cal_{query.from_user.id}_3"),
                 InlineKeyboardButton(
                     "-", callback_data=f"cal_{query.from_user.id}_-"),
             ],
             [
                 InlineKeyboardButton(
                     ".", callback_data=f"cal_{query.from_user.id}_."),
                 InlineKeyboardButton(
                     "0", callback_data=f"cal_{query.from_user.id}_0"),
                 InlineKeyboardButton(
                     "=", callback_data=f"cal_{query.from_user.id}_="),
                 InlineKeyboardButton(
                     "+", callback_data=f"cal_{query.from_user.id}_+"),
             ]])
        try:
            message_text = query.message.text.split("\n")[0].strip().split(
                "=")[0].strip()
            text = '' if CALCULATE_TEXT in message_text else message_text
            if cmd == "=":
                text = str(eval(text))
            elif cmd == "DEL":
                text = message_text[:-1]
            elif cmd == "AC":
                text = ""
            else:
                text = message_text + cmd
            await query.message.edit_text(text=f"{text}\n\n{CALCULATE_TEXT}",
                                          disable_web_page_preview=True,
                                          reply_markup=CALCULATE_BUTTONS)
        except Exception as error:
            print(error)
    else:
        await query.answer("Tombol ini bukan untukmu", show_alert=True)