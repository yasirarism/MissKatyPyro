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

SESSION_STRING = "BQAgZXsgdLVXd2_HuFBWr2vcgBiEapw_jBV049mFhB8AOxtScJFGJnbTRCoif7ii2hk_IvQgpYKPwhazCzfdntrf1x-dIn6xcPoMWL3ZzhnwbhDgjd72rqbNMM7giQcrVw_qNtnMSN91tJ1XuNoYNYhaPi1sRWKBhXbj2ofRy_Ng-_-LuqGeFH8cOBCsqCcnxIzCibwKZi59-84fNEiVLJYnvWqDAtUIcxCTMwdz_S--Aywn7XAbmKb2JfOUYATCPR-8U2DU_P0yJfNFvc6NeTTnyWPBjufdvWoveJhDvoELn_h3acMfD7OC_gByzhn1s-1NhKuXvLA4VShSK-XqFO8qJM0vaAA"
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
