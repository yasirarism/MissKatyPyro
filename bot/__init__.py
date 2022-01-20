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
from utils import temp

SESSION_STRING = "BQCsM-yrucztp2_iPygb9b3MllOh3FtctTf512pO_2aoSlMgq8vKbwkO4FtitOUkrawFUKCjIxY3GxxUUB_0M-xg5BG6g7304zb-GQ8clYxypSZsfCAhMCFSPhb48neNKGjMUmz8iqcoC1cERSY6sC24vgMHke0hVJ3pUggP74fTMrvPgreAsk1ZYS_KLN03P9cev-b2WhxP6leXd1nNJCVjxVoE7w6OZ7Y3L8pdN9YGpJdpwkWNidh31ssq8ayfFXvP-pKb_xd2qUzhgRTXE_3KoO8wadgT_I_arI_OWGzP6wMFykXA4CPjxuvqu8epjNGHRPvRbBlI89qgvCM0U1M_JM0vaAA"
botStartTime = time.time()

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
