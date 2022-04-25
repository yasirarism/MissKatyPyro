import logging
from unicodedata import name
from bot import app, user
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__, compose, Client

# Run Bot
if __name__ == "__main__":
    app.start()
    user.start()
    me = app.get_me()
    ubot = user.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    try:
        app.send_message(
            617426792,
            f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {ubot.first_name}\nBot: {me.first_name}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
        )
    except:
        pass
    logging.info(
        f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
    )
    idle()
    app.stop()
    user.stop()
    logging.info("Userbot and Bot stopped..")