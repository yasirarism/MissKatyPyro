# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import sys
from logging import getLogger
from os import environ

import dotenv

LOGGER = getLogger("MissKaty")

dotenv.load_dotenv("config.env", override=True)

YT_COOKIES = environ.get("YT_COOKIES")

if API_ID := environ.get("API_ID", ""):
    API_ID = int(API_ID)
else:
    LOGGER.error("API_ID variable is missing! Exiting now")
    sys.exit(1)
API_HASH = environ.get("API_HASH", "")
if not API_HASH:
    LOGGER.error("API_HASH variable is missing! Exiting now")
    sys.exit(1)
BOT_TOKEN = environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    LOGGER.error("BOT_TOKEN variable is missing! Exiting now")
    sys.exit(1)
DATABASE_URI = environ.get("DATABASE_URI", "")
if not DATABASE_URI:
    LOGGER.error("DATABASE_URI variable is missing! Exiting now")
    sys.exit(1)
if LOG_CHANNEL := environ.get("LOG_CHANNEL", ""):
    LOG_CHANNEL = int(LOG_CHANNEL)

else:
    LOGGER.error("LOG_CHANNEL variable is missing! Exiting now")
    sys.exit(1)
# Optional ENV
LOG_GROUP_ID = environ.get("LOG_GROUP_ID")
USER_SESSION = environ.get("USER_SESSION")
DATABASE_NAME = environ.get("DATABASE_NAME", "MissKatyDB")
TZ = environ.get("TZ", "Asia/Jakarta")
PORT = environ.get("PORT", 80)
COMMAND_HANDLER = environ.get("COMMAND_HANDLER", "! /").split()
SUDO = list(
    {
        int(x)
        for x in environ.get(
            "SUDO",
            "617426792 2024984460",
        ).split()
    }
)
OWNER_ID = int(environ.get("OWNER_ID", 2024984460))
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "YasirPediaChannel")
AUTO_RESTART = environ.get("AUTO_RESTART", False)
OPENAI_KEY = environ.get("OPENAI_KEY")
GOOGLEAI_KEY = environ.get("GOOGLEAI_KEY")
# 9Router (OpenAI-compatible gateway) untuk chatbot AI
NINE_ROUTER_API_KEY = environ.get("NINE_ROUTER_API_KEY")
NINE_ROUTER_BASE_URL = environ.get("NINE_ROUTER_BASE_URL", "https://9router.yasirweb.eu.org/v1")
NINE_ROUTER_MODEL_AI = environ.get("NINE_ROUTER_MODEL_AI", "oc/mimo-v2.5-free")
NINE_ROUTER_MODEL_ASK = environ.get("NINE_ROUTER_MODEL_ASK", "oc/deepseek-v4-flash-free")
PAYDISINI_KEY = environ.get("PAYDISINI_KEY")
PAYDISINI_CHANNEL_ID = environ.get("PAYDISINI_CHANNEL_ID", "17")

## Config For AUtoForwarder
# Forward From Chat ID
FORWARD_FROM_CHAT_ID = list(
    {
        int(x)
        for x in environ.get(
            "FORWARD_FROM_CHAT_ID",
            "-1001128045651 -1001455886928 -1001686184174",
        ).split()
    }
)
# Forward To Chat ID
FORWARD_TO_CHAT_ID = list(
    {int(x) for x in environ.get("FORWARD_TO_CHAT_ID", "-1001210537567").split()}
)
FORWARD_FILTERS = list(set(environ.get("FORWARD_FILTERS", "video document").split()))
BLOCK_FILES_WITHOUT_EXTENSIONS = bool(
    environ.get("BLOCK_FILES_WITHOUT_EXTENSIONS", True)
)
BLOCKED_EXTENSIONS = list(
    set(
        environ.get(
            "BLOCKED_EXTENSIONS",
            "html htm json txt php gif png ink torrent url nfo xml xhtml jpg",
        ).split()
    )
)
MINIMUM_FILE_SIZE = environ.get("MINIMUM_FILE_SIZE")
CURRENCY_API = environ.get("CURRENCY_API")
