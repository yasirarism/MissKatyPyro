import time
import pyromod
from logging import ERROR, INFO, FileHandler, StreamHandler, basicConfig, getLogger

from pyrogram import Client

from misskaty.vars import API_HASH, API_ID, BOT_TOKEN, USER_SESSION

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("MissKatyLogs.txt"), StreamHandler()],
    level=INFO,
)
getLogger("pyrogram").setLevel(ERROR)

MOD_LOAD = []
MOD_NOLOAD = []
HELPABLE = {}
cleanmode = {}
botStartTime = time.time()

# Pyrogram Bot Client
app = Client(
    "MissKatyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Pyrogram UserBot Client
user = Client(
    "YasirUBot",
    session_string=USER_SESSION,
)

app.start()
user.start()
bot = app.get_me()
ubot = user.get_me()
BOT_ID = bot.id
BOT_NAME = bot.first_name
BOT_USERNAME = bot.username
UBOT_ID = ubot.id
UBOT_NAME = ubot.first_name
UBOT_USERNAME = ubot.username
