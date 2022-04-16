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
from Python_ARQ import ARQ
from aiohttp import ClientSession
from utils import temp

SESSION_PYRO = "BQCOlR3PPl8vtmAiXZYJE5ZQVkY7GawBsfgnbrDa3ziiHYxO9z-qp62KpjLvwfkt3Abpatzli909ByMDKFQKovk31M7_M3CmbU6_udje3Ooab8lPIRZigGVxwFj9kwX4oF9u2l415ZBoe3Lhtwa0mh3X_VtC-IBtBfQ3KC5jMPnhUXYE48o38Z1zdb392H66JoSJazSGRsHxm07ZTFICSqq2zHRa_bfQrIc3dFsP1jp3E7_MQdsub8ZeUav_A3eC59495L5Qk1JXceo-X1SYT_SGpA-r0X9vaJ2ClRokgz8XIbSn222WTARWD0oB6rMTK3aYOXa5yAC2aQMIl78keXbtJM0vaAA"
botStartTime = time.time()

ARQ_API_URL = "https://arq.hamker.in/"
ARQ_API_KEY = "CYQWYJ-OMSAFJ-ARHIAT-SDADAX-ARQ"

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

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
    session_name=SESSION_PYRO,
    api_id=API_ID,
    api_hash=API_HASH,
)
