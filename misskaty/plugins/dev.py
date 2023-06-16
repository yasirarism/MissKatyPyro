import asyncio
import io
import os
import re
import sys
import html
import pickle
import json
import traceback
import cloudscraper
import aiohttp
from datetime import datetime
from shutil import disk_usage
from time import time
from database.users_chats_db import db
from inspect import getfullargspec
from typing import Any, Optional, Tuple

from psutil import cpu_percent, Process
from psutil import disk_usage as disk_usage_percent
from psutil import virtual_memory, cpu_count, boot_time, net_io_counters

from pyrogram import enums, filters, Client, __version__ as pyrover
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto
from pyrogram.raw.types import UpdateBotStopped
from pykeyboard import InlineKeyboard, InlineButton
from PIL import Image, ImageDraw, ImageFont

from misskaty import app, user, botStartTime, misskaty_version, BOT_NAME
from misskaty.helper.http import http
from misskaty.helper.eval_helper import meval, format_exception
from misskaty.helper.localization import use_chat_lang
from misskaty.helper.human_read import get_readable_file_size, get_readable_time
from misskaty.vars import COMMAND_HANDLER, SUDO, LOG_CHANNEL

__MODULE__ = "DevCommand"
__HELP__ = """
**For Owner Bot Only.**
/run [args] - Run eval CMD
/logs [int] - Check logs bot
/shell [args] - Run Exec/Terminal CMD
/download [link/reply_to_telegram_file] - Download file from Telegram
/disablechat [chat id] - Remove blacklist group
/enablechat [chat id] - Add Blacklist group
/banuser [chat id] - Ban user and block user so cannot use bot
/unbanuser [chat id] - Unban user and make their can use bot again

**For Public Use**
/stats - Check statistic bot
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
async def donate(client, ctx):
    keyboard = InlineKeyboard(row_width=2)
    keyboard.add(
        InlineButton('QR QRIS [Yasir Store]', url='https://telegra.ph/file/2acf7698f300ef3d9138f.jpg'),
        InlineButton('Sociabuzz', url='https://sociabuzz.com/yasirarism/tribe'),
        InlineButton('Saweria', url='https://saweria.co/yasirarism'),
        InlineButton('Trakteer', url='https://trakteer.id/yasir-aris-sp7cn'),
        InlineButton('Ko-Fi', url='https://ko-fi.com/yasirarism'),
        InlineButton('PayPal', url='https://paypal.me/yasirarism'),
    )
    await ctx.reply(
        f"Hai {ctx.from_user.mention}, jika kamu merasa bot ini besrguna bisa melakukan donasi dengan ke rekening diatas yaa (disarankan menggunakan QRIS atau Sociabuzz). Karena server bot ini menggunakan VPS dan tidaklah gratis. Terimakasih..\n\nHi {ctx.from_user.mention}, if you feel this bot is useful, you can make a donation to the account above (Use PayPal, SociaBuzz, or Ko-Fi). Because this bot server is hosted in VPS and not free. Thank you..", reply_markup=keyboard
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
    image = Image.open("assets/statsbg.jpg").convert("RGB")
    IronFont = ImageFont.truetype("assets/IronFont.otf", 42)
    draw = ImageDraw.Draw(image)

    def draw_progressbar(coordinate, progress):
        progress = 110 + (progress * 10.8)
        draw.ellipse((105, coordinate - 25, 127, coordinate), fill="#FFFFFF")
        draw.rectangle((120, coordinate, progress, coordinate - 25), fill="#FFFFFF")
        draw.ellipse(
            (progress - 7, coordinate - 25, progress + 15, coordinate), fill="#FFFFFF"
        )

    total, used, free = disk_usage(".")
    process = Process(os.getpid())

    botuptime = get_readable_time(time() - botStartTime)
    osuptime = get_readable_time(time() - boot_time())
    currentTime = get_readable_time(time() - botStartTime)
    botusage = f"{round(process.memory_info()[0]/1024 ** 2)} MB"

    upload = get_readable_file_size(net_io_counters().bytes_sent)
    download = get_readable_file_size(net_io_counters().bytes_recv)

    cpu_percentage = cpu_percent()
    cpu_counts = cpu_count()

    ram_percentage = virtual_memory().percent
    ram_total = get_readable_file_size(virtual_memory().total)
    ram_used = get_readable_file_size(virtual_memory().used)

    disk_percenatge = disk_usage("/").percent
    disk_total = get_readable_file_size(total)
    disk_used = get_readable_file_size(used)
    disk_free = get_readable_file_size(free)

    caption = f"<b>{BOT_NAME} {misskaty_version} is Up and Running successfully.</b>**OS Uptime:** {osuptime}\n<b>Bot Uptime:</b> <code>{currentTime}</code>\n**Bot Usage:** {botusage}\n\n**Total Space:** {disk_total}\n**Free Space:** {disk_free}\n\n**Download:** {download}\n**Upload:** {upload}\n\n<b>Pyrogram Version</b>: <code>{pyrover}</code>\n<b>Python Version</b>: <code>{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]} {sys.version_info[3].title()}</code>"

    start = datetime.now()
    msg = await message.reply_photo(
        photo="https://te.legra.ph/file/30a82c22854971d0232c7.jpg",
        caption=caption,
        quote=True,
    )
    end = datetime.now()

    draw_progressbar(243, int(cpu_percentage))
    draw.text(
        (225, 153),
        f"( {cpu_counts} core, {cpu_percentage}% )",
        (255, 255, 255),
        font=IronFont,
    )

    draw_progressbar(395, int(disk_percenatge))
    draw.text(
        (335, 302),
        f"( {disk_used} / {disk_total}, {disk_percenatge}% )",
        (255, 255, 255),
        font=IronFont,
    )

    draw_progressbar(533, int(ram_percentage))
    draw.text(
        (225, 445),
        f"( {ram_used} / {ram_total} , {ram_percentage}% )",
        (255, 255, 255),
        font=IronFont,
    )

    draw.text((335, 600), f"{botuptime}", (255, 255, 255), font=IronFont)
    draw.text(
        (857, 607),
        f"{(end-start).microseconds/1000} ms",
        (255, 255, 255),
        font=IronFont,
    )

    image.save("stats.png")
    await msg.edit_media(media=InputMediaPhoto("stats.png", caption=caption))
    os.remove("stats.png")


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
        await ctx.reply_msg(strings("no_reply"), del_in=5)


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
            "cloudscraper": cloudscraper,
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

    
@app.on_raw_update(group=-99)
async def updtebot(client, update, users, chats):
    if isinstance(update, UpdateBotStopped):
        user = users[update.user_id]
        if update.stopped and await db.is_user_exist(user.id):
            await db.delete_user(user.id)
        await client.send_msg(LOG_CHANNEL, f"<a href='tg://user?id={user.id}'>{user.first_name}</a> (<code>{user.id}</code>) " f"{'BLOCKED' if update.stopped else 'UNBLOCKED'} the bot at " f"{datetime.fromtimestamp(update.date)}")

async def aexec(code, c, m):
    exec("async def __aexec(c, m): " + "\n p = print" + "\n replied = m.reply_to_message" + "".join(f"\n {l_}" for l_ in code.split("\n")))
    return await locals()["__aexec"](c, m)


async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process
