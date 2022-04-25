import logging
import asyncio
from bot import app, user
from info import BOT_TOKEN
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__, compose


# Run Bot
async def main():
    await compose([app])


asyncio.run(main())
me = app.get_me()
user = user.get_me()
temp.ME = me.id
temp.U_NAME = me.username
temp.B_NAME = me.first_name
try:
    app.send_message(
        617426792,
        f"USERBOT AND BOT STARTED..\nUserBot: {user.first_name}\nBot: {me.first_name}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
    )
except:
    pass
logging.info(
    f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
)
logging.info(
    f"{user.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{user.username}."
)
