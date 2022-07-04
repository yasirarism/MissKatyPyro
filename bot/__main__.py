import sys
import glob
import asyncio
import logging
import importlib
from pathlib import Path
from pyrogram import idle
from bot import app, user, ptb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

ppath = "bot/plugins/*.py"
files = glob.glob(ppath)

loop = asyncio.get_event_loop()


async def start_services():
    print('\n')
    print('------------------- Initalizing Telegram Bot -------------------')
    await app.start()
    await user.start()
    await ptb.run_polling()
    print('----------------------------- DONE -----------------------------')
    print('\n')
    print('--------------------------- Importing ---------------------------')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"bot/plugins/{plugin_name}.py")
            import_path = f".plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(
                import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules[f"bot.plugins.{plugin_name}"] = load
            print(f"Imported => {plugin_name}")
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info(
            '----------------------- Service Stopped -----------------------')
