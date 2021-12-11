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
from utils import temp

SESSION_STRING = "BQA22ZytkOZ1cqUCfsQcqMnSWL6PWT6Rmv9oi35xKc3GvYbL2uHsURnHmBEm73uon5DWpX3AxI1Tb-eu28RB_60sQBVUvM8G6CEjOcgCk7Vu24w5MFBpfuumnCPYV8eLwFIQ-GROqA1aQvunSNYCh-vM4pXJ0A33VnmYBp7hKCMscAeVQ9OuKXIa65yrh1Uq0nvIXg5Ki7tt9Dz5mOkYdH44YAVFFpleffceWoVWrMPNf0CML1hVDDxquUskEuU81gG0FiigkiFRwoM6dmMtFCxKoawj-gdbkXr9KArz6bGN9G4bU48Lw5bNdaFKQKLjHIegnuHObAWJ89gPyq0qTwPAJM0vaAA"
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
