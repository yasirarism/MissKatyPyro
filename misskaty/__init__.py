from logging import basicConfig, FileHandler, StreamHandler, INFO
import time
from pyrogram import Client
from misskaty.vars import API_ID, API_HASH, BOT_TOKEN, USER_SESSION

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("MissKatyLogs.txt"), StreamHandler()],
    level=INFO,
)

MOD_LOAD = []
MOD_NOLOAD = []
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
