import time
from re import findall, MULTILINE
from asyncio import Lock
from pyrogram import filters
from misskaty.vars import COMMAND_HANDLER
from misskaty import app, botStartTime
from misskaty.helper.human_read import get_readable_time
from subprocess import run as srun


@app.on_message(filters.command(["ping"], COMMAND_HANDLER))
async def ping(_, message):
    currentTime = get_readable_time(time.time() - botStartTime)
    start_t = time.time()
    rm = await message.reply_text("🐱 Pong!!...")
    end_t = time.time()
    time_taken_s = round(end_t - start_t, 3)
    try:
        await rm.edit(
            f"<b>🐈 MissKatyBot online.</b>\n\n<b>Ping:</b> <code>{time_taken_s} detik</code>\n<b>Uptime:</b> <code>{currentTime}</code>"
        )
    except Exception:
        pass


@app.on_message(filters.command(["ping_dc"], COMMAND_HANDLER))
async def ping_handler(_, message):
    m = await message.reply("Pinging datacenters...")
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
                resp_time = findall(r"time=.+m?s", shell.stdout, MULTILINE)[0].replace(
                    "time=", ""
                )

                text += f"    **{dc.upper()}:** {resp_time} ✅\n"
            except Exception:
                # There's a cross emoji here, but it's invisible.
                text += f"    **{dc.upper}:** ❌\n"
        await m.edit(text)
