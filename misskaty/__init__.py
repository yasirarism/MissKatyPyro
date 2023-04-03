import os
import time
from logging import ERROR, INFO, FileHandler, StreamHandler, basicConfig, getLogger, handlers

import pyromod.listen
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from pymongo import MongoClient
from pyrogram import Client

from misskaty.vars import API_HASH, API_ID, BOT_TOKEN, DATABASE_URI, USER_SESSION, TZ

basicConfig(filename="MissKatyLogs.txt", format="%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s", level=INFO)

logger = getLogger()
# handler logging dengan batasan 100 baris
handler = handlers.RotatingFileHandler("MissKatyLogs.txt", maxBytes=1024 * 1024)
handler.setLevel(INFO)
logger.addHandler(handler)
getLogger("pyrogram").setLevel(ERROR)
getLogger("openai").setLevel(ERROR)

MOD_LOAD = []
MOD_NOLOAD = ["subscene_dl"]
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

pymonclient = MongoClient(DATABASE_URI)

jobstores = {"default": MongoDBJobStore(client=pymonclient, database="MissKatyDB", collection="nightmode")}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=TZ)

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
