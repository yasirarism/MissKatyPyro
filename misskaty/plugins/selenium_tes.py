import os
import chromedriver_autoinstaller
from pyrogram import filters
from misskaty import app
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err


@app.on_message(filters.command(["pahe"], COMMAND_HANDLER))
@capture_err
async def pahe(clinet, msg):
    chromedriver_autoinstaller.install()
    os.chmod("/MissKaty/chromedriver", 755)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    wd = webdriver.Chrome("/MissKaty/chromedriver", chrome_options=chrome_options)
    wd.get("https://pahe.li/")
    print(wd.page_source)
