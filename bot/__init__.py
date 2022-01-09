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

SESSION_STRING = "BQB8sbV37GuxSg-BV4ocoqT4hQbBn2dEiAsuO6UOCqXm4mvefSYXiydQ_q2MTTXzNVWNhS9Rq2hH6PpRzBY_rcJjqiLmkZdnN1L5PW1bHgtzrv0fqNTbml8yeVpfM3DtwG0_SqWGFFWnBMkCmlLdcZYEEigsKY4dsv_UcjTix0ZRLEdCfN8SQYbqEXFiA-ojxNAQluOHyYBOJ9FURry0-e3D8zyr59HhVugnC8vcoyXYabY9bnR_d6S01FperEIXeIQgawi-xolR24auv59wghWZJ-0r-941jFAHSmy-vYpzHZn8PrtujccDA-eRN6_JM0jnsqsWROeAGDtp2taEtwdHJM0vaAA"
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
