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

SESSION_PYRO = "BQBQ_xDmq4KXSuBug3_i4lVvZpebiVStEXCKcyNtv81FdHIhVbomoq4qfqn3xUycVTfziHfVhRCrBqKqBne1DaDixWB-sHZGeRlj8iXneCWUq-al7GuXzHolA4bGDi7NydZw1EqBJoyqKoiswfhhBqZwCBWmXURbbpCxit_CjW0E5fWSczoktR16EZQKnJWZq_5DBmwxz0cyqqiKrA7yAeAfT73iJfQ3j6A8D8LSxZUiro78zQSiGabIusKXa5PVbnyHpYS-9Wd5wieW18bGKzIlHWggb1MGTHLhL_B2hLo_v_t0QxOT3TueyDPd64TqzcWszh0eqd1FDRFGQvUsXFPSJM0vaAA"
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
