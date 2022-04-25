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

SESSION_PYRO = "BQAP-GEAZy4yLP1XyJ1aJ08DOgrT9KZpGvyhXv069mJjRVboPxN74z7jI4xpDMh89EXPLj_7UyI3nBoF-nvrZNRxo_gP6QwCY-IEfIHhuSo8A0ABI02gXjJoeZmxfADXIgv9S4tn6ndX3FlouX6bw_hI9l_hmr7tCRCBTWhUR7lkl1kPkARw7sDud7V63FcWIq_-IA_piqDLQISH5lNi3S1I1CtyIVJT41I7GvjwcUqZAIcVsYr-01aguECSHfcwXHwdSpfQeB_FZYeErM5Y3sYkrx3BvhCMmWr8BW5R_Kq6PHBGn0OW4_uTo9ENGhBpNC4uJZahDgBSAircT5fv7c8bBl9W4AAAAAAkzS9oAA"
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
