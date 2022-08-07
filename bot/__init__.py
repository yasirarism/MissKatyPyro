import logging
import time
import subprocess
import logging.config
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
from pyrogram import Client, __version__
from info import API_ID, API_HASH, BOT_TOKEN
from Python_ARQ import ARQ
from aiohttp import ClientSession
from utils import temp
from pyromod import listen

SESSION_PYRO = "BQAP-GEATby3DBNNTJn5UyrtcLj23-zikswHWtnKT4GVyW7Ace7UgQIszh0omGSwFVdM-Quz4a8P6-blmwTkeOf8vgZgtNyRvJNPvl7X02QklT7HpSYs9tBuScpQvqJFltwo0_8xm0sFlO3k0MccyMKic4Ba1JY4LiufsIhjd2BWkY1H-rk-cHiPvd_sJwUJgXn6gTsRVJ0xecHVTMi9QgxwMfMg9M2gtcu6vOMj-hYK23yIPHsrnmwpo36AvqdaWalgH3o9XkLdBSxsNS80z5-lwmG712D4W9JN_ON5dp5qUjsXf8ayGoqazQ_ALcUj922I53BIYluYUV7kTrZQPUlGMtSSkAAAAAAkzS9oAA"
botStartTime = time.time()

ARQ_API_URL = "https://arq.hamker.in/"
ARQ_API_KEY = "GLDKXS-UDKRKL-GDVISK-COZFRF-ARQ"

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

subprocess.Popen(f"gunicorn bot.web.wserver:app --bind 0.0.0.0", shell=True)

# Pyrogram Bot Client
app = Client(
    "MissKatyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    plugins=dict(root="bot/plugins"),
    sleep_threshold=5,
)

# Pyrogram UserBot Client
user = Client(
    "YasirUBot",
    session_string=SESSION_PYRO,
)
