import os
from sys import executable, argv
from bot import app
from pyrogram import filters
from info import ADMINS, COMMAND_HANDLER, HEROKU_APP


@app.on_message(filters.command(["restart", "restart@MissKatyRoBot"], COMMAND_HANDLER) & filters.user(ADMINS))
async def restart(client, message):
    a = await message.reply("Ok, Let me restart!")
    if HEROKU_APP is None:
        await a.edit(text="Restarting Bot & Userbot ...")
        # https://stackoverflow.com/a/57032597/15215201
        os.execl(executable, executable, *argv)
    else:
        await a.edit(text="Restarting Heroku Dyno ...")
        HEROKU_APP.restart()
