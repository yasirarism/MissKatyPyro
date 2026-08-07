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

import uvicorn
from pyrogram import __version__, idle
from pyrogram.raw.all import layer

from misskaty import (
    BOT_NAME,
    BOT_USERNAME,
    HELPABLE,
    UBOT_NAME,
    app,
    scheduler,
)
from misskaty.helper.cleanmode import auto_clean
from misskaty.helper.ytdl_helper import ensure_yt_cookies
from misskaty.plugins import ALL_MODULES
from misskaty.plugins.web_scraper import web
from misskaty.vars import OWNER_ID, PORT, USER_SESSION

LOGGER = getLogger("MissKaty")


async def run_wsgi():
    from misskaty.core.web import api

    config = uvicorn.Config(api, host="0.0.0.0", port=int(PORT))
    server = uvicorn.Server(config)
    await server.serve()


class BotBootstrap:
    async def load_modules(self):
        for module in ALL_MODULES:
            imported_module = importlib.import_module(f"misskaty.plugins.{module}")
            if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
                if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                    HELPABLE[imported_module.__MODULE__.lower()] = imported_module

    @staticmethod
    def build_modules_table() -> str:
        bot_modules = ""
        j = 1
        for module in ALL_MODULES:
            if j == 4:
                bot_modules += "|{:<15}|\n".format(module)
                j = 0
            else:
                bot_modules += "|{:<15}".format(module)
            j += 1
        return bot_modules

    async def send_online_status(self, bot_modules: str):
        try:
            LOGGER.info("[INFO]: SENDING ONLINE STATUS")
            if USER_SESSION:
                await app.send_message(
                    OWNER_ID,
                    f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {UBOT_NAME}\nBot: {BOT_NAME}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{BOT_USERNAME}.\n\n<code>{bot_modules}</code>",
                )
            else:
                await app.send_message(
                    OWNER_ID,
                    f"BOT STARTED with Pyrogram v{__version__}..\nBot: {BOT_NAME}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{BOT_USERNAME}.\n\n<code>{bot_modules}</code>",
                )
        except Exception as e:
            LOGGER.error(str(e))

    async def init_web_collection(self):
        db = app.db
        if "web" not in await db.list_collection_names():
            webdb = db["web"]
            for key, value in web.items():
                await webdb.insert_one({key: value})

    async def handle_restart_message(self):
        if os.path.exists("restart.pickle"):
            with open("restart.pickle", "rb") as status:
                chat_id, message_id = pickle.load(status)
            os.remove("restart.pickle")
            await app.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="<b>Bot restarted successfully!</b>",
            )

    async def start(self):
        await self.load_modules()
        bot_modules = self.build_modules_table()

        LOGGER.info("+===============================================================+")
        LOGGER.info("|                        MissKatyPyro                           |")
        LOGGER.info("+===============+===============+===============+===============+")
        LOGGER.info(bot_modules)
        LOGGER.info("+===============+===============+===============+===============+")
        LOGGER.info("[INFO]: BOT STARTED AS @%s!", BOT_USERNAME)

        await ensure_yt_cookies()
        await self.send_online_status(bot_modules)

        scheduler.start()
        asyncio.create_task(run_wsgi())
        await self.init_web_collection()
        await self.handle_restart_message()
        asyncio.create_task(auto_clean())
        await idle()


def main():
    bootstrap = BotBootstrap()
    try:
        asyncio.get_event_loop().run_until_complete(bootstrap.start())
        app.loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception:
        LOGGER.info(traceback.format_exc())
    finally:
        app.loop.stop()
        LOGGER.info("------------------------ Stopped Services ------------------------")
