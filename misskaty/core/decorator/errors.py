import asyncio
import traceback
from functools import wraps

from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from misskaty import app
from misskaty.vars import LOG_CHANNEL


def split_limits(text):
    if len(text) < 2048:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    result.append(small_msg)

    return result


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            return await app.leave_chat(message.chat.id)
        except Exception as err:
            exc = traceback.format_exc()
            error_feedback = split_limits(
                "**ERROR** | `{}` | `{}`\n\n```{}```\n\n```{}```\n".format(
                    message.from_user.id if message.from_user else 0,
                    message.chat.id if message.chat else 0,
                    message.text or message.caption,
                    exc,
                )
            )

            for x in error_feedback:
                try:
                    await app.send_message(LOG_CHANNEL, x)
                    await message.reply(x)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
            raise err

    return capture
