import logging
from bot import app
from pyrogram.raw.all import layer
from pyrogram import idle, __version__

# Run Bot
if __name__ == "__main__":
    app.start()
    me = app.get_me()
    logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    idle()
