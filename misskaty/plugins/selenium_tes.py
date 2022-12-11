import os
import chromedriver_autoinstaller
from logging import getLogger
from pyrogram import filters
from misskaty import app
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from selenium import webdriver

LOGGER = getLogger(__name__)


@app.on_message(filters.command(["pahe"], COMMAND_HANDLER))
@capture_err
async def pahe(_, msg):
    # chromedriver_autoinstaller.install()
    os.chmod("/MissKaty/chromedriver", 755)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        options=chrome_options, executable_path="/MissKaty/chromedriver"
    )
    driver.get("https://pahe.li/")
    LOGGER.info(driver.page_source)
