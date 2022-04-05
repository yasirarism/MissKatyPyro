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

SESSION_PYRO = "BQCnFr2Oe51ATtnrrtGJM5PbUVsQYxn6lEdoX1_4bG1ocMSbOicltC_RKcmVidgVDgtwaSuLx6k7gYAPIuTmdDQmEFb-DMsL-WDguywGNYh1m-Ny9xpuvCOPKVV_TsE4MbOrCdNQSMKrIcSxZ8bFnndCu20lrcLaPZFpAH3WXMAgJZtpnIh_PSVCt4p9wqMVl94HIPZw6EBAEovpD9JxfNM5DIYNHXfGElCA6MYmDw1tUEf332Kf8OJiHTDLu7g9RZSFbDZVx0kelNDt5psLMe8HD9_8FIGJfTAZ8uuWNnCHBtlgKc1skh6bhbgh897OTbIzfinq_JhkhHwSP2I_stFUJM0vaAA"
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
