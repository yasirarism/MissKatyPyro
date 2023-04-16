"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import os
import time
from asyncio import Lock
from re import MULTILINE, findall
from subprocess import run as srun

from pyrogram import Client, filters
from pyrogram.types import Message

from misskaty import app, botStartTime
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper.http import http
from misskaty.helper.human_read import get_readable_time
from misskaty.vars import COMMAND_HANDLER

from .dev import shell_exec


@app.on_message(filters.command(["ping"], COMMAND_HANDLER))
@ratelimiter
async def ping(self: Client, ctx: Message):
    if os.path.exists(".git"):
        botVersion = (await shell_exec("git log -1 --date=format:v%y.%m%d.%H%M --pretty=format:%cd"))[0]
    else:
        botVersion = "v2.49"
    try:
        serverinfo = await http.get("https://ipinfo.io/json")
        org = serverinfo.json()["org"]
    except:
        org = "N/A"
    currentTime = get_readable_time(time.time() - botStartTime)
    start_t = time.time()
    rm = await ctx.reply_msg("🐱 Pong!!...")
    end_t = time.time()
    time_taken_s = round(end_t - start_t, 3)
    await rm.edit_msg(f"<b>🐈 MissKatyBot {botVersion} online.</b>\n\n<b>Ping:</b> <code>{time_taken_s} detik</code>\n<b>Uptime:</b> <code>{currentTime}</code>\nHosted by <code>{org}</code>")


@app.on_message(filters.command(["ping_dc"], COMMAND_HANDLER))
@ratelimiter
async def ping_handler(self: Client, ctx: Message):
    m = await ctx.reply_msg("Pinging datacenters...")
    async with Lock():
        ips = {
            "dc1": "149.154.175.53",
            "dc2": "149.154.167.51",
            "dc3": "149.154.175.100",
            "dc4": "149.154.167.91",
            "dc5": "91.108.56.130",
        }
        text = "**Pings:**\n"

        for dc, ip in ips.items():
            try:
                shell = srun(
                    ["ping", "-c", "1", "-W", "2", ip],
                    text=True,
                    check=True,
                    capture_output=True,
                )
                resp_time = findall(r"time=.+m?s", shell.stdout, MULTILINE)[0].replace("time=", "")

                text += f"    **{dc.upper()}:** {resp_time} ✅\n"
            except Exception:
                # There's a cross emoji here, but it's invisible.
                text += f"    **{dc.upper}:** ❌\n"
        await m.edit_msg(text)
