import logging
from bot import app, user
from info import BOT_TOKEN
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__

# Run Bot
if __name__ == "__main__":
    app.start()
    user.start()
    idle()
    app.stop()
    user.stop()
