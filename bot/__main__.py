import logging
from bot import app, user, telethon
from info import BOT_TOKEN
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__

# Run Bot
if __name__ == "__main__":
    app.start()
    user.start()
    telethon.start(bot_token=BOT_TOKEN)
    me = app.get_me()
    user = user.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    app.send_message(617426792, f"USERBOT AND BOT STARTED..\nUserBot: {user.first_name}\nBot: {me.first_name}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
    logging.info(f"{user.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{user.username}.")
    idle()
