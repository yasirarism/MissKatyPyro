import os, subprocess
from sys import executable
from bot import app, user
from pyrogram import filters
from info import ADMINS, COMMAND_HANDLER

@app.on_message(filters.command(["restart","restart@MissKatyRoBot"], COMMAND_HANDLER) & filters.user(ADMINS))
async def restart(client, message):
    await message.reply("Restarting, Please wait!")
    await app.stop()
    await user.stop()
    # os.execl(executable, executable, "-m", "bot")
    os.execl("/bin/sh", "/start.sh")
