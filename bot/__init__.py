import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from pyrogram import Client
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN
from bot.plugins import all_plugins

BOT_USERNAME = ""
BOT_NAME = ""
BOT_ID = 0


async def get_self(c):
    """Gets the information about bot."""
    global BOT_USERNAME, BOT_NAME, BOT_ID
    getbot = await c.get_me()
    BOT_NAME = getbot.first_name
    BOT_USERNAME = getbot.username
    BOT_ID = getbot.id
    return getbot

class YasirBot(Client):
    """Starts the Pyrogram Client on the Bot Token when we do 'python3 -m alita'"""

    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            session_name=SESSION,
            bot_token=BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
            api_id=API_ID,
            api_hash=API_HASH,
            workers=50,
        )

    async def start(self):
        """Start the bot."""
        await super().start()

        meh = await get_self(self)  # Get bot info from pyrogram client

        # Show in Log that bot has started
        LOGGER.info(
            f"Pyrogram v{__version__} (Layer - {layer}) started on @{meh.username}",
        )
        LOGGER.info(f"Python Version: {python_version()}\n")

        LOGGER.info("Bot Started Successfully!\n")

    async def stop(self):
        await super().stop()
        LOGGER.info("Bot Stopped")
