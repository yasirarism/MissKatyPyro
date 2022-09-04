import logging, asyncio, importlib
from uvloop import install
from bot import app, user
from bot.plugins import ALL_MODULES
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__
from subprocess import Popen
from contextlib import closing, suppress

loop = asyncio.get_event_loop()

HELPABLE = {}


# Run Bot
async def start_bot():
    global HELPABLE

    for module in ALL_MODULES:
        imported_module = importlib.import_module(f"bot.plugins.{module}")
        if (hasattr(imported_module, "__MODULE__")
                and imported_module.__MODULE__):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (hasattr(imported_module, "__HELP__")
                    and imported_module.__HELP__):
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
    await app.start()
    await user.start()
    me = await app.get_me()
    ubot = await user.get_me()
    print("+===============================================================+")
    print("|                        MissKatyPyro                           |")
    print("+===============+===============+===============+===============+")
    print(bot_modules)
    print("+===============+===============+===============+===============+")
    print(f"[INFO]: BOT STARTED AS @{me.username}!")

    try:
        print("[INFO]: SENDING ONLINE STATUS")
        await app.send_message(
            617426792,
            f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {ubot.first_name}\nBot: {me.first_name}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
        )
    except Exception:
        pass

    await idle()
    await app.stop()
    await user.stop()
    print("[INFO]: Bye!")


if __name__ == "__main__":
    install()
    with closing(loop):
        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(start_bot())
        loop.run_until_complete(asyncio.sleep(3.0))
