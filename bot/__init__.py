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
from telethon import TelegramClient
from Python_ARQ import ARQ
from aiohttp import ClientSession
from utils import temp

SESSION_STRING = "BQCWhJPeI7P0GAuDZ9rPoBWx0F-xVztjjYBx2DlfkvE3tdHt8qHd9fxI-kCMm4Lj9do4ad7ZnUc76erdfz3sJQjmg8ptm7tDYBMFvwuiUCwsiiGgaG4Xf80183v8yLHG2bC0qbVo-yrC_aRKK6QFN4RO_ny5M4SlVLnUxbFe7E9Y96WtV-6GO2pw9RxXoMSA5NjN5x__xV9FVqJErmYpJrQMJN9yofxnG74GWQNfu1NoS2CbShnF-ecNTCqTISV-ovHFTmV3dAi3t8EyHp6jrw14N2hhdaTCUyqxSwYD9XHTYOIxlk7N65Riey1t5BcwhJrVxHHlR7lJQZzKzCrBPLMGJM0vaAA"
botStartTime = time.time()

ARQ_API_URL = "https://thearq.tech/"
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
    session_name=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH,
)

telethon = TelegramClient("Telethon Bot", API_ID, API_HASH)
