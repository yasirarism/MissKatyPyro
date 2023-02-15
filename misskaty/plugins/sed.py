# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import html

import regex
from pyrogram import filters
from pyrogram.errors import MessageEmpty

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter


@app.on_message(filters.regex(r"^s/(.+)?/(.+)?(/.+)?") & filters.reply)
@ratelimiter
async def sed(c, m):
    exp = regex.split(r"(?<![^\\]\\)/", m.text)
    pattern = exp[1]
    replace_with = exp[2].replace(r"\/", "/")
    flags = exp[3] if len(exp) > 3 else ""

    rflags = 0

    count = 0 if "g" in flags else 1
    if "i" in flags and "s" in flags:
        rflags = regex.I | regex.S
    elif "i" in flags:
        rflags = regex.I
    elif "s" in flags:
        rflags = regex.S

    text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return

    try:
        res = regex.sub(pattern, replace_with, text, count=count, flags=rflags, timeout=1)
    except TimeoutError:
        return await m.reply_text("Oops, your regex pattern has run for too long.")
    except regex.error as e:
        return await m.reply_text(str(e))
    else:
        try:
            await c.send_message(
                m.chat.id,
                f"<pre>{html.escape(res)}</pre>",
                reply_to_message_id=m.reply_to_message.id,
            )
        except MessageEmpty:
            return await m.reply_text("Please reply message to use this feature.")
        except Exception as e:
            return await m.reply_text(f"ERROR: {str(e)}")
