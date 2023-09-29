"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
 """
import asyncio
import importlib
import os
import pickle
import traceback
from logging import getLogger

from pyrogram import __version__, idle
from pyrogram.raw.all import layer

from database import dbname
from misskaty import BOT_NAME, BOT_USERNAME, HELPABLE, UBOT_NAME, app, scheduler, get_event_loop
from misskaty.plugins import ALL_MODULES
from misskaty.plugins.web_scraper import web
from misskaty.vars import SUDO, USER_SESSION
from utils import auto_clean

LOGGER = getLogger("MissKaty")


# Run Bot
async def start_bot():
    for module in ALL_MODULES:
        imported_module = importlib.import_module(f"misskaty.plugins.{module}")
        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            imported_module.__MODULE__ = imported_module.__MODULE__
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "|{:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "|{:<15}".format(i)
        j += 1
    LOGGER.info("+===============================================================+")
    LOGGER.info("|                        MissKatyPyro                           |")
    LOGGER.info("+===============+===============+===============+===============+")
    LOGGER.info(bot_modules)
    LOGGER.info("+===============+===============+===============+===============+")
    LOGGER.info("[INFO]: BOT STARTED AS @%s!", BOT_USERNAME)

    try:
        LOGGER.info("[INFO]: SENDING ONLINE STATUS")
        for i in SUDO:
            if USER_SESSION:
                await app.send_message(
                    i,
                    f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {UBOT_NAME}\nBot: {BOT_NAME}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{BOT_USERNAME}.\n\n<code>{bot_modules}</code>",
                )
            else:
                await app.send_message(
                    i,
                    f"BOT STARTED with Pyrogram v{__version__} as {BOT_NAME}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{BOT_USERNAME}.\n\n<code>{bot_modules}</code>",
                )
    except Exception as e:
        LOGGER.error(str(e))
    scheduler.start()
    if "web" not in await dbname.list_collection_names():
        webdb = dbname["web"]
        for key, value in web.items():
            await webdb.insert_one({key: value})
    if os.path.exists("restart.pickle"):
        with open("restart.pickle", "rb") as status:
            chat_id, message_id = pickle.load(status)
        os.remove("restart.pickle")
        await app.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="<b>Bot restarted successfully!</b>",
        )
    asyncio.create_task(auto_clean())
    await idle()


if __name__ == "__main__":
    try:
        get_event_loop().run_until_complete(start_bot())
        app.loop.run_forever()
        # loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception:
        err = traceback.format_exc()
        LOGGER.info(err)
    finally:
        loop.stop()
        LOGGER.info(
            "------------------------ Stopped Services ------------------------"
        )
