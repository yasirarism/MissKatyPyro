import logging
import time
import logging.config

# Get logging
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
from pyrogram import Client
from bot.vars import API_ID, API_HASH, BOT_TOKEN, USER_SESSION

MOD_LOAD = []
MOD_NOLOAD = []
SUDO = [617426792, 2024984460]
HELPABLE = {}

SESSION_PYRO = "AgD4NZsAT5Grbqm0QF1byf6IyKTrOe-225NXLb8QoewMiFzJkX-RieZjojz6XeVL1psCBEhPCt5xwTqeSg-PlTwesMlCfpiaCZ5EBVnDd_zXFSvClOVQUDYTZ4WYE4ZwiszMDShv74PG5G1lxCzYVhZZwFg4QELsJY6P4es8ctRknfdgbov-rck5UhbYrGkgKyM3LaZOgUczBIZuPeQp2Z56l1t78yjUBEaUi1G3zFWQUdxjffq5FbmB26clLo7QhxUErmAU5QXnvhuIWmZYKL_ts-N8uyX0GYUBCiPbAlgSmdpclWENJRNHGKyYMffLkfV2_bwvBMOVs3DbYqggukeVJEXsLgAAAAB4ss-MAA"
botStartTime = time.time()

# Pyrogram Bot Client
app = Client(
    name="MissKatyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=5,
)

# Pyrogram UserBot Client
user = Client(
    name="YasirUBot",
    session_string=USER_SESSION,
)
