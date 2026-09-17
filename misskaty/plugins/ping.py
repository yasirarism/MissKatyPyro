"""
* @author        yasir <yasiramunandar@gmail.com>
* @date          2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

import platform
import time
from asyncio import Lock
from re import MULTILINE, findall
from subprocess import run as srun

from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.types import Message

from misskaty import app, botStartTime, misskaty_version
from misskaty.helper.human_read import get_readable_time
from misskaty.vars import COMMAND_HANDLER

PING_LOCK = Lock()


@app.on_message(filters.command(["ping"], COMMAND_HANDLER))
async def ping(_, ctx: Message):
    currentTime = get_readable_time(time.time() - botStartTime)
    start_t = time.time()
    rm = await ctx.reply("<emoji id=\"5474618190271104037\">🐱</emoji> Pong!!...")
    end_t = time.time()
    time_taken_s = round(end_t - start_t, 3)
    await rm.edit(
        f"<b><emoji id=\"5474618190271104037\">🐱</emoji> MissKatyBot {misskaty_version} based Pyrogram {pyrover} Online.</b>\n\n"
        f"<b><emoji id=\"5877613700344450910\">⏲</emoji> Ping:</b> <code>{time_taken_s} detik</code>\n"
        f"<b><emoji id=\"5877410604225924969\">🔄</emoji> Uptime:</b> <code>{currentTime}</code>\n"
        f"<b><emoji id=\"5260480440971570446\">💻</emoji> Python:</b> <code>{platform.python_version()}</code>"
    )


@app.on_message(filters.command(["ping_dc"], COMMAND_HANDLER))
async def ping_handler(_, ctx: Message):
    m = await ctx.reply("Pinging datacenters...")
    async with PING_LOCK:
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
                resp_time = findall(r"time=.+m?s", shell.stdout, MULTILINE)[0].replace(
                    "time=", ""
                )

                text += f"    **{dc.upper()}:** {resp_time} ✅\n"
            except Exception:
                # There's a cross emoji here, but it's invisible.
                text += f"    **{dc.upper}:** ❌\n"
        await m.edit(text)
