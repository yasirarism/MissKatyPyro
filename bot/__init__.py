import logging
import time
import logging.config
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN
from telethon import TelegramClient
from utils import temp

SESSION_STRING = "BQC_BtOKA43B47S4bVMcIkca3QPMTFHgTXbd80muKdn3q8yyyhZmanVVay5mSKn1MlGdMO-0z4Dd7SoYxgpzNlmVuYRpIpVpDwJCwZmBLHR-vNoRkPp6zJ2VwyawZbKdFTERGjWM_hlPaNF3xw3E5jLz_5PB4jiH7XDIMGkM361w7fjslbRi73Pm3j3E4qOwnBbrAUDitjARtri7t5ERZsgYixBZ2-t7dHOOJvW4ELK6s8xeQr8RDX7vu0gs-2l_HBrc2LLYvF5gu7hoq9JhPXC8OTEdld5P09QQ1qstuyUfoc5GphW9x3nmDhUsHinZJ-dNJmrsffMDxlSu7tgT6sTfJM0vaAA"
botStartTime = time.time()

app = Client(
    session_name=SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    plugins=dict(root="bot/plugins"),
    sleep_threshold=5,
)

user = Client(
    session_name=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH,
)

telethon = TelegramClient("Telethon Bot", API_ID, API_HASH)
