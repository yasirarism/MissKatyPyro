import os
import time
from logging import ERROR, INFO, StreamHandler, basicConfig, getLogger, handlers

from misskaty.core import misskaty_patch
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from pymongo import MongoClient
from pyrogram import Client

from misskaty.vars import API_HASH, API_ID, BOT_TOKEN, DATABASE_URI, USER_SESSION, TZ

basicConfig(
    level=INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s.%(funcName)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler("MissKatyLogs.txt", mode="w+", maxBytes=1000000),
        StreamHandler(),
    ],
)
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
BOT_ID = app.me.id
BOT_NAME = app.me.first_name
BOT_USERNAME = app.me.username
UBOT_ID = user.me.id
UBOT_NAME = user.me.first_name
UBOT_USERNAME = user.me.username
