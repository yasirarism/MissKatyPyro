import asyncio
import html
import io
import json
import os
import pickle
import re
import sys
import traceback
from datetime import datetime
from inspect import getfullargspec
from shutil import disk_usage
from time import time
from typing import Any, Optional, Tuple

import aiohttp
import cfscrape
from psutil import cpu_percent
from psutil import disk_usage as disk_usage_percent
from psutil import virtual_memory
from pyrogram import Client, enums, filters
from pyrogram.raw.types import UpdateBotStopped
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import BOT_NAME, app, botStartTime, user
from misskaty.helper.eval_helper import format_exception, meval
from misskaty.helper.http import http
from misskaty.helper.human_read import (get_readable_file_size,
                                        get_readable_time)
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER, SUDO, LOG_CHANNEL

__MODULE__ = "DevCommand"
__HELP__ = """
**For Owner Bot Only.**
/run [args] - Run eval CMD
/shell [args] - Run Exec/Terminal CMD
/download [link/reply_to_telegram_file] - Download file from Telegram

**For Public Use**
/json - Send structure message Telegram in JSON using Pyrogram Style.
"""

var = {}
teskode = {}


async def edit_or_reply(msg, **kwargs):
    func = msg.edit if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command(["logs"], COMMAND_HANDLER) & filters.user(SUDO))
@use_chat_lang()
async def log_file(self: Client, ctx: Message, strings) -> "Message":
    """Send log file"""
    msg = await ctx.reply_msg("<b>Reading bot logs ...</b>")
    if len(ctx.command) == 1:
        await ctx.reply_document(
            "MissKatyLogs.txt",
            caption="Log Bot MissKatyPyro",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            strings("cl_btn"),
                            f"close#{ctx.from_user.id}",
                        )
                    ]
                ]
            ),
        )
        await msg.delete_msg()
    elif len(ctx.command) == 2:
        val = ctx.text.split()
        tail = await shell_exec(f"tail -n {val[1]} -v MissKatyLogs.txt")
        await msg.edit_msg(f"<pre language='bash'>{html.escape(tail[0])}</pre>")
    else:
        await msg.edit_msg("Unsupported parameter")


@app.on_message(filters.command(["donate"], COMMAND_HANDLER))
async def donate(_, message):
    await message.reply_photo(
        "https://telegra.ph/file/2acf7698f300ef3d9138f.jpg",
        caption=f"Hai {message.from_user.mention}, jika kamu merasa bot ini berguna bisa melakukan donasi dengan scan kode QRIS diatas yaa. Terimakasih..",
    )


@app.on_message(filters.command(["balas"], COMMAND_HANDLER) & filters.user(SUDO) & filters.reply)
async def balas(self: Client, ctx: Message) -> "str":
    pesan = ctx.input
    await ctx.delete_msg()
    await ctx.reply_msg(pesan, reply_to_message_id=ctx.reply_to_message.id)


@app.on_message(filters.command(["stats"], COMMAND_HANDLER))
async def server_stats(self: Client, ctx: Message) -> "Message":
    """
    Give system stats of the server.
    """
    if os.path.exists(".git"):
        botVersion = (await shell_exec("git log -1 --date=format:v%y.%m%d.%H%M --pretty=format:%cd"))[0]
    else:
        botVersion = "v2.49"
    try:
        serverinfo = await http.get("https://ipinfo.io/json")
        org = serverinfo.json()["org"]
    except:
        org = "N/A"
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free = disk_usage(".")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    neofetch = (await shell_exec("neofetch --stdout"))[0]
    caption = f"""
**{BOT_NAME} {botVersion} is Up and Running successfully.**
<b>Bot Uptime:</b> `{currentTime}`
<b>Server:</b> <code>{org}</code>
<b>Total Disk Space:</b> `{total}`
<b>Used:</b> `{used}({disk_usage_percent("/").percent}%)`
<b>Free:</b> `{free}`
<b>CPU Usage:</b> `{cpu_percent()}%`
<b>RAM Usage:</b> `{virtual_memory().percent}%`

`{neofetch}`
"""
    await ctx.reply_msg(caption)


@app.on_message(filters.command(["shell", "sh", "term"], COMMAND_HANDLER) & filters.user(SUDO))
@app.on_edited_message(filters.command(["shell", "sh", "term"], COMMAND_HANDLER) & filters.user(SUDO))
@user.on_message(filters.command(["shell", "sh", "term"], ".") & filters.me)
@use_chat_lang()
async def shell(self: Client, ctx: Message, strings) -> "Message":
    if len(ctx.command) == 1:
        return await edit_or_reply(ctx, text=strings("no_cmd"))
    msg = await ctx.edit_msg(strings("run_exec")) if ctx.from_user.is_self else await ctx.reply_msg(strings("run_exec"))
    shell = (await shell_exec(ctx.input))[0]
    if len(shell) > 3000:
        with io.BytesIO(str.encode(shell)) as doc:
            doc.name = "shell_output.txt"
            await ctx.reply_document(
                document=doc,
                caption=f"<code>{ctx.input[: 4096 // 4 - 1]}</code>",
                file_name=doc.name,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=strings("cl_btn"),
                                callback_data=f"close#{ctx.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
            await msg.delete_msg()
    elif len(shell) != 0:
        await edit_or_reply(
            ctx,
            text=html.escape(shell),
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("cl_btn"), callback_data=f"close#{ctx.from_user.id}")]]),
        )
        if not ctx.from_user.is_self:
            await msg.delete_msg()
    else:
        await ctx.reply(strings("no_reply"), del_in=5)


@app.on_message((filters.command(["ev", "run", "myeval"], COMMAND_HANDLER) | filters.regex(r"app.run\(\)$")) & filters.user(SUDO))
@app.on_edited_message((filters.command(["ev", "run", "myeval"]) | filters.regex(r"app.run\(\)$")) & filters.user(SUDO))
@user.on_message(filters.command(["ev", "run", "myeval"], ".") & filters.me)
@use_chat_lang()
async def cmd_eval(self: Client, ctx: Message, strings) -> Optional[str]:
    if (ctx.command and len(ctx.command) == 1) or ctx.text == "app.run()":
        return await edit_or_reply(ctx, text=strings("no_eval"))
    status_message = await ctx.edit_msg(strings("run_eval")) if ctx.from_user.is_self else await ctx.reply_msg(strings("run_eval"), quote=True)
    code = ctx.text.split(" ", 1)[1] if ctx.command else ctx.text.split("\napp.run()")[0]
    out_buf = io.StringIO()
    out = ""
    humantime = get_readable_time

    async def _eval() -> Tuple[str, Optional[str]]:
        # Message sending helper for convenience
        async def send(*args: Any, **kwargs: Any) -> Message:
            return await ctx.reply_msg(*args, **kwargs)

        # Print wrapper to capture output
        # We don't override sys.stdout to avoid interfering with other output
        def _print(*args: Any, **kwargs: Any) -> None:
            if "file" not in kwargs:
                kwargs["file"] = out_buf
            return print(*args, **kwargs)

        eval_vars = {
            "self": self,
            "humantime": humantime,
            "ctx": ctx,
            "var": var,
            "teskode": teskode,
            "re": re,
            "os": os,
            "asyncio": asyncio,
            "cfscrape": cfscrape,
            "json": json,
            "aiohttp": aiohttp,
            "print": _print,
            "send": send,
            "stdout": out_buf,
            "traceback": traceback,
            "http": http,
            "replied": ctx.reply_to_message,
        }
        eval_vars.update(var)
        eval_vars.update(teskode)
        try:
            return "", await meval(code, globals(), **eval_vars)
        except Exception as e:  # skipcq: PYL-W0703
            # Find first traceback frame involving the snippet
            first_snip_idx = -1
            tb = traceback.extract_tb(e.__traceback__)
            for i, frame in enumerate(tb):
                if frame.filename == "<string>" or frame.filename.endswith("ast.py"):
                    first_snip_idx = i
                    break
            # Re-raise exception if it wasn't caused by the snippet
            # Return formatted stripped traceback
            stripped_tb = tb[first_snip_idx:]
            formatted_tb = format_exception(e, tb=stripped_tb)
            return "⚠️ Error while executing snippet\n\n", formatted_tb

    before = time()
    prefix, result = await _eval()
    after = time()
    # Always write result if no output has been collected thus far
    if not out_buf.getvalue() or result is not None:
        print(result, file=out_buf)
    el_us = after - before
    try:
        el_str = get_readable_time(el_us)
    except:
        el_str = "1s"
    if not el_str or el_str is None:
        el_str = "0.1s"

    out = out_buf.getvalue()
    # Strip only ONE final newline to compensate for our message formatting
    if out.endswith("\n"):
        out = out[:-1]
    final_output = f"{prefix}<b>INPUT:</b>\n<pre language='python'>{html.escape(code)}</pre>\n<b>OUTPUT:</b>\n<pre language='python'>{html.escape(out)}</pre>\nExecuted Time: {el_str}"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(out)) as out_file:
            out_file.name = "MissKatyEval.txt"
            await ctx.reply_document(
                document=out_file,
                caption=f"<code>{code[: 4096 // 4 - 1]}</code>",
                disable_notification=True,
                thumb="assets/thumb.jpg",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=strings("cl_btn"),
                                callback_data=f"close#{ctx.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
            await status_message.delete_msg()
    else:
        await edit_or_reply(
            ctx,
            text=final_output,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings("cl_btn"), callback_data=f"close#{ctx.from_user.id}")]]),
        )
        if not ctx.from_user.is_self:
            await status_message.delete_msg()


# Update and restart bot
@app.on_message(filters.command(["update"], COMMAND_HANDLER) & filters.user(SUDO))
@use_chat_lang()
async def update_restart(self: Client, ctx: Message, strings) -> "Message":
    try:
        out = (await shell_exec("git pull"))[0]
        if "Already up to date." in str(out):
            return await ctx.reply_msg(strings("already_up"))
        await ctx.reply_msg(f"<code>{out}</code>")
    except Exception as e:
        return await ctx.reply_msg(str(e))
    msg = await ctx.reply_msg(strings("up_and_rest"))
    with open("restart.pickle", "wb") as status:
        pickle.dump([ctx.chat.id, msg.id], status)
    os.execvp(sys.executable, [sys.executable, "-m", "misskaty"])


@app.on_raw_update(filters.private, group=-99)
async def updtebot(client, update, users, chats):
    if isinstance(update, UpdateBotStopped):
        user = users[update.user_id]
        await client.send_msg(LOG_CHANNEL, f"{user.mention} ({user.id}) "
              f"{'BLOCKED' if update.stopped else 'UNBLOCKED'} the bot at "
              f"{datetime.fromtimestamp(update.date)}")


async def aexec(code, c, m):
    exec("async def __aexec(c, m): " + "\n p = print" + "\n replied = m.reply_to_message" + "".join(f"\n {l_}" for l_ in code.split("\n")))
    return await locals()["__aexec"](c, m)


async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process
