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

SESSION_PYRO = "BQAP-GEAEHO9g6CChvc8KVbc2yrw2E1HNOZLXstnj0s8LRRLZuz2YTbnCTk1ByIe-9c2X02lSjaO9zwtS-ajVrTIhBLXjnQ2DKUgrKnEiOAcTHuw3cImzPs-LBOrQ1YmVBaVqPYCdPlxFGeRo7djaNOwRMOlPzn29Ofoa3IxFbxeixktp9iqynvGsSUuxFoveiIpXMlH4mX1HNPYEUwFd3qppSeEOuJ1d92oZ5asMfOFwXSdpu93EGldw93gnFrgHL0QSBwga-dhAUBrpSJivlyg0Xn1mwCTpzerCvsQR-ptgWcLYiYGyVr_a6Y0Msgi1TVuLKu275A6Edqk83apORQmQSU6AQAAAAAkzS9oAA"
botStartTime = time.time()

ARQ_API_URL = "https://arq.hamker.in/"
ARQ_API_KEY = "CYQWYJ-OMSAFJ-ARHIAT-SDADAX-ARQ"

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

app = Client(
    SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    plugins=dict(root="bot/plugins"),
    sleep_threshold=5,
)

user = Client(
    SESSION_PYRO,
    api_id=API_ID,
    api_hash=API_HASH,
)
