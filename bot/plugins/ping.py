import time
from pyrogram import filters
from info import COMMAND_HANDLER
from bot import app, user, botStartTime
from bot.utils.human_read import get_readable_time
from subprocess import check_output

@app.on_message(filters.command(["ping","ping@MissKatyRoBot"], COMMAND_HANDLER))
async def ping(_, message):
    last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'"], shell=True).decode()
    botVersion = check_output(["git log -1 --date=format:v%y.%m%d.%H%M --pretty=format:%cd"], shell=True).decode()
    currentTime = get_readable_time(time.time() - botStartTime)
    start_t = time.time()
    rm = await message.reply_text("🐱 Pong!!...")
    end_t = time.time()
    time_taken_s = round(end_t - start_t, 3)
    try:
        await rm.edit(f"<b>🐈 MissKaty {botVersion} online.</b> (<b>Last Commit:</b> <code>{last_commit}</code>)\n\n<b>Ping:</b> <code>{time_taken_s} detik</code>\n<b>Uptime:</b> <code>{currentTime}</code>", disable_web_page_preview=True)
    except Exception:
        pass
