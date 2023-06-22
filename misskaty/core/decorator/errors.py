import asyncio
import os
import traceback
from functools import wraps, partial
from datetime import datetime

from pyrogram.types import CallbackQuery
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from misskaty import app
from misskaty.vars import LOG_CHANNEL


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        if isinstance(message, CallbackQuery):
            sender = partial(message.answer, show_alert=True)
            chat = message.message.chat
        else:
            sender = message.reply_text
            chat = message.chat
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            return await app.leave_chat(message.chat.id)
        except Exception as err:
            exc = traceback.format_exc()
            error_feedback = "ERROR | {} | {}\n\n{}\n\n{}\n".format(
                    message.from_user.id if message.from_user else 0,
                    chat.id if chat else 0,
                    message.text or message.caption,
                    exc,
            )
            day = datetime.today()
            tgl_now = datetime.now()

            cap_day = f"{day.strftime('%A')}, {tgl_now.strftime('%d %B %Y %H:%M:%S')}"
            await sender.reply("😭 An Internal Error Occurred while processing your Command, the Logs have been sent to the Owners of this Bot. Sorry for Inconvenience...")
            with open(f"crash_{tgl_now.strftime('%d %B %Y')}.txt", "w+", encoding="utf-8") as log:
                log.write(error_feedback)
                log.close()
            await app.send_document(
                LOG_CHANNEL, f"crash_{tgl_now.strftime('%d %B %Y')}.txt", caption=f"Crash Report of this Bot\n{cap_day}"
            )
            os.remove(f"crash_{tgl_now.strftime('%d %B %Y')}.txt")
            raise err

    return capture
