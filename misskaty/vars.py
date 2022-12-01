import logging
from os import environ
from dotenv import load_dotenv

load_dotenv("config.env", override=True)

LOGGER = logging.getLogger(__name__)

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
    log_error(f"One or more env variables missing! Exiting now.\n{e}")
    exit(1)
COMMAND_HANDLER = environ.get("COMMAND_HANDLER", "! /").split()
SUDO = ["617426792, 2024984460"]
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "YasirPediaChannel")
