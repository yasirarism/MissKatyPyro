import time
from bot import app
from datetime import datetime
from bot.utils.decorator import capture_err
from info import COMMAND_HANDLER
from pyrogram import filters
from bot.utils.pyro_progress import (
    progress_for_pyrogram,
    humanbytes,
)

@app.on_message(filters.command(["download","download@MissKatyRoBot"], COMMAND_HANDLER) & filters.user(617426792))
@capture_err
async def download(client, message):
    pesan = await message.reply_text("Processing...", quote=True)
    if message.reply_to_message is not None:
        start_t = datetime.now()
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            progress=progress_for_pyrogram,
            progress_args=("trying to download, sabar yakk..", pesan, c_time),
        )
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await pesan.edit(
            f"Downloaded to <code>{the_real_download_location}</code> in <u>{ms}</u> seconds."
        )
    else:
        await pesan.edit("Reply to a Telegram Media, to download it to my local server.")
