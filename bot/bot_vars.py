from bot import app

async def aboutbot():
    me = await app.get_me()
    BOT_ID = me.id
    BOT_NAME = me.first_name
    BOT_USERNAME = me.username
