import logging
import time
import logging.config
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
from pyrogram import Client, __version__
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, DATABASE_URI
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from Python_ARQ import ARQ
from aiohttp import ClientSession
from utils import temp
from pyromod import listen

mongo = MongoClient("DATABASE_URI")
db_afk = mongo.AFKDB

SESSION_PYRO = "BQAP-GEAIrX-3t8x38eLFBtivMLR3PHq_GCksEgxGzwt-4hvxDlpaxuCQIApN7D37MNlNnNmbKcZomwXccD9icHnXKlhhe_6dDlIkn63cYm4yDTLZodTFkKgRh60399kpnQhOHZltqbI2KVhDU7Xhg-TLRBp1YTpZis4Sia1jGX0CaFY0YvHC3sG6YyidAOU-9pD5sESjcu29F4d-drt6TeD9yihEhhLZOV7K1sEcFeT5CiY-bHPTBH9uqWTMcg6pJXR-yzYqWppazng6n-bQmEHCsUOasjw_mVlkHaOe-WTNLWHZQpjdsY8MSogaWAZvp8LvkjIwFwYN7Y-JbNMksGRYKOyWwAAAAAkzS9oAA"
botStartTime = time.time()

ARQ_API_URL = "https://arq.hamker.in/"
ARQ_API_KEY = "GLDKXS-UDKRKL-GDVISK-COZFRF-ARQ"

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
)

user = Client(
    "YasirUBot",
    session_string=SESSION_PYRO,
)
