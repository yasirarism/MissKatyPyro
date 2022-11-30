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

SESSION_PYRO = "AgD4NZsAT5Grbqm0QF1byf6IyKTrOe-225NXLb8QoewMiFzJkX-RieZjojz6XeVL1psCBEhPCt5xwTqeSg-PlTwesMlCfpiaCZ5EBVnDd_zXFSvClOVQUDYTZ4WYE4ZwiszMDShv74PG5G1lxCzYVhZZwFg4QELsJY6P4es8ctRknfdgbov-rck5UhbYrGkgKyM3LaZOgUczBIZuPeQp2Z56l1t78yjUBEaUi1G3zFWQUdxjffq5FbmB26clLo7QhxUErmAU5QXnvhuIWmZYKL_ts-N8uyX0GYUBCiPbAlgSmdpclWENJRNHGKyYMffLkfV2_bwvBMOVs3DbYqggukeVJEXsLgAAAAB4ss-MAA"

# Required ENV
try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    API_ID = getConfig("API_ID")
    API_HASH = getConfig("API_HASH")
    # MongoDB information
    DATABASE_URI = getConfig("DATABASE_URI")
    DATABASE_NAME = getConfig("DATABASE_NAME")
    LOG_CHANNEL = int(getConfig("LOG_CHANNEL"))
    USER_SESSION = environ.get("USER_SESSION", SESSION_PYRO)
except Exception as e:
    log_error(f"One or more env variables missing! Exiting now.\n{e}")
    exit(1)
COMMAND_HANDLER = environ.get("COMMAND_HANDLER", "! /").split()
SUDO = ["617426792, 2024984460"]
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "YasirPediaChannel")