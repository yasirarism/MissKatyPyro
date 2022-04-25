import logging
import time
import logging.config
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
from pyrogram import Client, __version__, enums
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN
from Python_ARQ import ARQ
from aiohttp import ClientSession
from utils import temp

SESSION_PYRO = "BQCqknvhk_pwkA9yzwaJExMKUP4LyvCqnU1zJB6MpLobEQvH-kWdMek-D6WSDxpy6BZWVvFXa_dRvF-iGg4OoY5PpWRlPLxMbOpmdnzCp5wxuqqMKBhnUqohiorQv2HmsqQumK9wa6_nb_zwcAuGLgfqB3l5pLL39rj55-n8lYGsz8W_5kV-ng2PkcwWTaiZQhAjbTvtxuCp4xA4wPEjj_fhBqh1Trm0bZNjdDjh34LLIcpdOYjpU_VBJ_rpDoZLOONQQUpx24kf_lGocEC1sOucsBN6OT2OHcudtFJ56_19yxTlJfsbz5vOQgY2Fkum1QYvibudRLfL38PMtyZnoW3eJM0vaAA"
botStartTime = time.time()

ARQ_API_URL = "https://arq.hamker.in/"
ARQ_API_KEY = "CYQWYJ-OMSAFJ-ARHIAT-SDADAX-ARQ"

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

app = Client(
    "MissKatyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    plugins=dict(root="bot/plugins"),
    sleep_threshold=5,
    parse_mode=enums.ParseMode.HTML,
)

user = Client(
    "YasirUBot",
    session_string=str(SESSION_PYRO),
    api_id=API_ID,
    api_hash=API_HASH,
)
