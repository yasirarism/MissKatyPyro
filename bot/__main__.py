import logging, asyncio
from aiohttp import web
from bot import app, user
from utils import temp
from pyrogram.raw.all import layer
from pyrogram import idle, __version__

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({
        "status": "Berjalan",
        "maintained_by": "@YasirArisM",
        "telegram_bot": '@' + (await app.get_me()).username,
        "Bot Version": "3.0.1"
    })

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app


loop = asyncio.get_event_loop()


# Run Bot
async def start_services():
    await app.start()
    await user.start()
    webs = web.AppRunner(await web_server())
    await webs.setup()
    await web.TCPSite(webs, "0.0.0.0").start()
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
