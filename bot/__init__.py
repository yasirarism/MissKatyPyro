import logging
import time
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

SESSION_PYRO = "BQAkiwCTRYEZ1B1-Oz1_HZk3s9-U_YPzlrsDzGotCOSvBMnVE6Ov-S8L9UBvT1eXoR4PInYZrbAz--JZFzmpXC_IM5LcQgyBizKa_70tbUlsemy8ocj3H7pPOlnhO2odEI_J8m8_d1xM1_IccxSjcY9zapAEVtuhtb4xhYTibDVPaaSNgzPk7B2ryOny7xZ2nvcK819yuZw84j7gm-WlDepNZKIS1CtkC4yu5ZZwIHFEo4d5hwAr1lOPJcM0Q2ppAMoqnjZYwc6R1ODQaS_EKr_bBNVbpQN0S8-hogfb9qa8h_mye6evZ9jNV6NCmKgD_kx7sTWhH2BZVzwPP7pt3Th_JM0vaAA"
botStartTime = time.time()

ARQ_API_URL = "https://arq.hamker.in/"
ARQ_API_KEY = "GLDKXS-UDKRKL-GDVISK-COZFRF-ARQ"

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

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
