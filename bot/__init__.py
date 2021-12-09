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

SESSION_STRING = "BQBz7VSKz3nEXaDNJtyyCDfNLKqqYlnGFfNA3j9jymLHGqyH2Ag0EGKm1mMp7Lffk22bzwTif7qcrD9ybGd7GY_GklemOfAEv_GrC8IxMfF-oqY3Bg8lzobhXnvxOZtmlZjE-ZZVSANT7rt4KvohBYA4tY_JpZDLCWgBf_An1snfhYQCVW7_njVbfIf8OJ8TRqYAbfb4-T7YkPrFMdkOidUwhn32OtfBPmB6HoBQRmRZzI-V2JSkAbZdsZPRgNJN9-t8v3flz6PRoV1WBB1OtLZ5ruxiyXWwdYh_CzrMumQpfT7o94NcQEeyMinFf8H23D-2bf4U5izxzk5hdKUnhPA9JM0vaAA"
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
