# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import os
import time
from asyncio import get_event_loop
from faulthandler import enable as faulthandler_enable
from logging import ERROR, INFO, StreamHandler, basicConfig, getLogger, handlers

import uvloop, uvicorn
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from async_pymongo import AsyncClient
from pymongo import MongoClient
from pyrogram import Client
from web.webserver import api

from misskaty.vars import (
    API_HASH,
    API_ID,
    BOT_TOKEN,
    DATABASE_NAME,
    DATABASE_URI,
    PORT,
    TZ,
    USER_SESSION,
)

basicConfig(
    level=INFO,
    format="[%(levelname)s] - [%(asctime)s - %(name)s - %(message)s] -> [%(module)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler(
            "MissKatyLogs.txt", mode="w+", maxBytes=5242880, backupCount=1
        ),
        StreamHandler(),
    ],
)
getLogger("pyrogram").setLevel(ERROR)
getLogger("openai").setLevel(ERROR)
getLogger("httpx").setLevel(ERROR)
getLogger("iytdl").setLevel(ERROR)

MOD_LOAD = []
MOD_NOLOAD = ["subscene_dl"]
HELPABLE = {}
cleanmode = {}
botStartTime = time.time()
misskaty_version = "v2.16.1"

uvloop.install()
faulthandler_enable()
from misskaty.core import misskaty_patch

# Pyrogram Bot Client
app = Client(
    "MissKatyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    mongodb=dict(connection=AsyncClient(DATABASE_URI), remove_peers=True),
    sleep_threshold=180,
    app_version="MissKatyPyro Stable",
    workers=50,
    max_concurrent_transmissions=4,
)
app.db = AsyncClient(DATABASE_URI)
app.log = getLogger("MissKaty")

# Pyrogram UserBot Client
user = Client(
    "YasirUBot",
    session_string=USER_SESSION,
    mongodb=dict(connection=AsyncClient(DATABASE_URI), remove_peers=False),
    sleep_threshold=180,
    app_version="MissKaty Ubot",
)

jobstores = {
    "default": MongoDBJobStore(
        client=MongoClient(DATABASE_URI), database=DATABASE_NAME, collection="nightmode"
    )
}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=TZ)

async def run_wsgi():
    config = uvicorn.Config(api, host="0.0.0.0", port=int(PORT))
    server = uvicorn.Server(config)
    await server.serve()

app.start()
BOT_ID = app.me.id
BOT_NAME = app.me.first_name
BOT_USERNAME = app.me.username
if USER_SESSION:
    try:
        user.start()
        UBOT_ID = user.me.id
        UBOT_NAME = user.me.first_name
        UBOT_USERNAME = user.me.username
    except Exception as e:
        app.log.error(f"Error while starting UBot: {e}")
        UBOT_ID = None
        UBOT_NAME = None
        UBOT_USERNAME = None
else:
    UBOT_ID = None
    UBOT_NAME = None
    UBOT_USERNAME = None
