import logging
from bot import app, user
from info import BOT_TOKEN
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__, Client

# Run Bot
if __name__ == "__main__":
    app = Client(
        "MissKatyBot",
        workers=50,
        plugins=dict(root="bot/plugins"),
        sleep_threshold=5,
    )

    user = Client("YasirUBot")
    app.start()
    user.start()
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
    idle()
    app.stop()
    user.stop()
    logging.info("Userbot and Bot stopped..")
