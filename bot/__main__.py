import logging
import asyncio
from bot import app, user
from info import BOT_TOKEN
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__, compose

# Run Bot
#async def main():
#    await compose([app, user])

# asyncio.run(main())

import asyncio
from pyrogram import Client, idle


async def main():
    apps = [Client("MissKatyBot"), Client("YasirUbot")]

    ...  # Set up handlers

    for app in apps:
        await app.start()

    await idle()

    for app in apps:
        await app.stop()


asyncio.run(main())