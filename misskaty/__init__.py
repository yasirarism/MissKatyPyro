import logging
import time
import logging.config

# Get logging
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
from pyrogram import Client
from misskaty.vars import API_ID, API_HASH, BOT_TOKEN, USER_SESSION

MOD_LOAD = []
MOD_NOLOAD = []
SUDO = [617426792, 2024984460]
HELPABLE = {}

botStartTime = time.time()

# Pyrogram Bot Client
app = Client(
    name="MissKatyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=5,
)

# Pyrogram UserBot Client
user = Client(
    name="YasirUBot",
    session_string=USER_SESSION,
)
