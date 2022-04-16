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

SESSION_PYRO = "BQAhjWRzkjQxqVDpPd6p27d0PWsM99DsfN-VwQ93DIID2wuwvit6DWpextCm3Wj_EUSWDDR_z6P7lQ-wOzkqlp-wtA9E_uo2n2mGQ6F3ksgsUynm9yt379loXouCGLDd9102YPEX8mo33uRa0By-fM6aMBN2cmm5kgCSawHo9heNTElBJ5L5magHwLCH6SPMS5g8483BeBtAmJ7SV20-yAnkL-ZWJmLPJlXANlyYBdZy43BVmMDKDEkAQzNrAAXCDuVzn1RtAbnoBV9xELKGmOVTF4yIMGCm52l-Aln5R3hpmXHxlZpudr_N2J8uLPa2j_CfdDgGGgb7_AONjqkmvdo0JM0vaAA"
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
