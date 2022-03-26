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

SESSION_PYRO = "BQALhNMAzK4u-c_-4CgfomVKJvkDBs5wWgBLWntboOIeNtu1XD-jnJIj6kyP3IJRZilcWl1KhyJnWoIeVAQbROsTSXEKoq9TvXKl43t4cxkFG73zQfdtAJT3heSW3deLBouZTOEeerG-4n6WPorLO8yrO0ZWQXN744T-KEiJZQsSoZglTAJIbt6V2NJJQmlEzS9779jAYJLbZP7IhGhxM81R2sOjg0u4u8gPIqKgR2IIZwmGaJ7kc5VMgmMSvP-6m1ebapK-C__SEbzqYi8FYtjZUJO77eRF7HPOvmM4rvkMycnr-VmHPxJIJ3D_y0gjFM3DsJ8q7w4VKB2yfQCTfR_5JM0vaAA"
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
