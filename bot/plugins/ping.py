import time
from pyrogram import filters
from bot import app, COMMAND_HANDLER

@app.on_message(filters.command("ping", COMMAND_HANDLER))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("🐱 Pong!!...")
    end_t = time.time()
    time_taken_s = round(end_t - start_t, 3)
    await rm.edit(f"<b>🐈 Pong!</b>\n<code>{time_taken_s} detik</code>")
