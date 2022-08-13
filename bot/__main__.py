import logging, asyncio, threading
from bot import app, user, loop
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__

from web.wserver import web


# Run Bot
async def start_services():

    me = await app.get_me()
    ubot = await user.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    try:
        await app.send_message(
            617426792,
            f"USERBOT AND BOT STARTED with Pyrogram v{__version__}..\nUserBot: {ubot.first_name}\nBot: {me.first_name}\n\nwith Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
        )
    except:
        pass
    logging.info(
        f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
    )
    await idle()
    await app.stop()
    await ubot.stop()


if __name__ == '__main__':
    app.start()
    user.start()
    threading.Thread(target=start_services).start()
    loop.run_forever()
