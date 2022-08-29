""" WRITTEN BY @pokurt, https://github.com/pokurt"""

import asyncio
import traceback
from functools import wraps
from threading import Thread
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from info import LOG_CHANNEL
from bot import app


def asyncify(func):
    async def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        func_out = await loop.run_in_executor(None, func, *args, **kwargs)
        return func_out

    return inner


def split_limits(text):
    if len(text) < 4096:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 4096:
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
            await app.leave_chat(message.chat.id)
            return
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
                await app.send_message(LOG_CHANNEL, x)
                await message.reply(x)
            raise err

    return capture


def new_thread(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""

    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper
