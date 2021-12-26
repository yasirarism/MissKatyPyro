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

SESSION_STRING = "BQAgpCukd2qCITQXeGlTD5ERryFLNJZtL_uxlpMdHQifPOG-STbh4FMXJJi-sq9Q8fK49ptAUkewjkldOFrkeD4MffXUL7ByPQXOwYZQ4vCsSiKMEF44j0hbboZASz2ImYy2lFUtRpmeRre-kbdHRBFx1bX2NXAfsXKyQy7LUhZQCU3TdwZIRQpxzA6d15osugQ8ofJ5LaJNj7xrLVvYEzXxVhl9HyQ5wlK8qYUhrvOKSopgK1J1KmEVk4jwgBpKraLCii76RYojtpf0KZwLsUT8mGtzXKUjl5_m320b4W-ECUW2jlsKe6f_qgmKnyqinYPDK1ZatouWvQxpVriUMRbPJM0vaAA"
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
