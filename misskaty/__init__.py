import time
from logging import ERROR, INFO, StreamHandler, basicConfig, getLogger, handlers

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pyrogram import Client

from database.session_db import MongoStorage
from misskaty.core import misskaty_patch
from misskaty.vars import API_HASH, API_ID, BOT_TOKEN, DATABASE_URI, TZ, USER_SESSION

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
misskaty_version = "v2.023.5.16 - Stable"

pymonclient = MongoClient(DATABASE_URI)
mongo = AsyncIOMotorClient(DATABASE_URI)

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

jobstores = {"default": MongoDBJobStore(client=pymonclient, database="MissKatyDB", collection="nightmode")}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=TZ)

app.start()
if USER_SESSION:
    user.start()
    UBOT_ID = user.me.id
    UBOT_NAME = user.me.first_name
    UBOT_USERNAME = user.me.username
else:
    None, None, None = UBOT_ID, UBOT_NAME, UBOT_USERNAME
BOT_ID = app.me.id
BOT_NAME = app.me.first_name
BOT_USERNAME = app.me.username
