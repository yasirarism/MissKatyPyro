import sys, requests
from logging import getLogger
from os import environ
from dotenv import load_dotenv

LOGGER = getLogger(__name__)

def getConfig(name: str):
    try:
        return environ[name]
    except:
        return ""

# Required ENV
try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    API_ID = getConfig("API_ID")
    API_HASH = getConfig("API_HASH")
    # MongoDB information
    DATABASE_URI = getConfig("DATABASE_URI")
    DATABASE_NAME = getConfig("DATABASE_NAME")
    LOG_CHANNEL = int(getConfig("LOG_CHANNEL"))
    USER_SESSION = getConfig("USER_SESSION")
except Exception as e:
    LOGGER.error(f"One or more env variables missing! Exiting now.\n{e}")
    sys.exit(1)
    
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
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "YasirPediaChannel")
NIGHTMODE = environ.get("NIGHTMODE", False)
OPENAI_API = getConfig("OPENAI_API")

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
FORWARD_TO_CHAT_ID = list({int(x) for x in environ.get("FORWARD_TO_CHAT_ID", "-1001210537567").split()})
FORWARD_FILTERS = list(set(environ.get("FORWARD_FILTERS", "video document").split()))
BLOCK_FILES_WITHOUT_EXTENSIONS = bool(environ.get("BLOCK_FILES_WITHOUT_EXTENSIONS", True))
BLOCKED_EXTENSIONS = list(
    set(
        environ.get(
            "BLOCKED_EXTENSIONS",
            "html htm json txt php gif png ink torrent url nfo xml xhtml jpg",
        ).split()
    )
)
MINIMUM_FILE_SIZE = environ.get("MINIMUM_FILE_SIZE", None)
