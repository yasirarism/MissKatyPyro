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
from telethon.sessions import StringSession
from Python_ARQ import ARQ
from aiohttp import ClientSession
from utils import temp

SESSION_PYRO = "BQB8sTuxz_Zroi-S_eEa3UqixsAh1VcX2u1DppoJjra-mF1PekV_fhlEZ6RiFoi0zaFtXqrK7OykwYuqU0kPJM6GQxk_wAutnhTQnY-xebxItME6psc_qhODVWGWJYq3O5bCxc57UxpGfdSgN908ipw7OuIX5iYCW9bC8qaNyQKE9A9QLdOZfu1hbL8Lk7cUygSL_2YFCRM7oOXcL4VXAUnZoC-rbkgM7p8QYVZ8lJBqFG8EW7Whqj6uQTHGxwOhIXE2AgJiEQsO5Ml9WmCpzuiYXtLmN-KsOb-f-_JBJsUB1hE42VU0R6KTBFbjy9o4rslXWJLacK-0Lzf6A7JHX7ULJM0vaAA"
SESSION_TELETHON ="1BVtsOLIBuwrHc8uZl7wZgvTAYnXnUGkV7cNY6AWcLovB2nBgEmv98suuH2aC26SvF5fQkSUo0gsZOLoXxKlebyIJypumfLE6tOCm5N-y-8CVHjlYx0p1-xPT2wmQw4lCUKSZ9UfUAfZuPybHyPVvmd5np7I25VyTWd-4KWT_Ln7QIABk5GAdbLjj1Fx1Feh_MIF8HvO_pRGEieMfsHZc5OG6IBDjqGBXQV0r8omGtSXSR25397Mr4Nwj5R3T92_cZ3gzfPkNhn1GwgKhpry7ynTuhUDQP0r1YOrDoRXRZIVktwpEJTvmBNUMEcnCUpPe0E15Jfp_OUIzTAMZeApjgFM029ZM8OU="
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
    session_name=SESSION_PYRO,
    api_id=API_ID,
    api_hash=API_HASH,
)

telethon = TelegramClient("Telethon Bot", API_ID, API_HASH)
telethon_ubot = TelegramClient(StringSession(SESSION_TELETHON), API_ID, API_HASH)
