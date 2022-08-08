import logging, asyncio
from bot import app, user
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__

loop = asyncio.get_event_loop()


# Run Bot
async def start_services():
    await app.start()
    await user.start()
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
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info(
            '----------------------- Service Stopped -----------------------')
