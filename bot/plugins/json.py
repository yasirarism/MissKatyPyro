import os, json
from pyrogram import filters
from bot import ptb, app
from info import COMMAND_HANDLER
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


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
        await message.reply_document(document="json.text",
                                     caption=str(e),
                                     disable_notification=True,
                                     reply_to_message_id=reply_to_id)
        os.remove("json.text")


async def json_ptb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    the_real_message = None
    reply_to_id = None

    the_real_message = update.message.reply_to_message or update.message
    try:
        await update.message.reply_html(
            f"<code>{json.dumps(the_real_message, indent=2, ensure_ascii=False)}</code>"
        )
    except Exception as e:
        with open("json.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await update.message.reply_document(document="json.text",
                                            caption=str(e),
                                            disable_notification=True,
                                            reply_to_message_id=reply_to_id)
        os.remove("json.text")


ptb.add_handler(CommandHandler("json_ptb", json_ptb))