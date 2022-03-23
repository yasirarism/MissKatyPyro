import os
from sys import executable
from bot import app
from pyrogram import filters
from info import ADMINS

@app.on_message(filters.command(["restart","restart@MissKatyRoBot"], COMMAND_HANDLER) & filters.user(ADMINS))
async def restart(client, message):
    await message.reply("Restarting, Please wait!")
    os.execl(executable, executable, "-m", "bot")
