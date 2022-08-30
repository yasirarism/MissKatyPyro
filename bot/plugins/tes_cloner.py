from bot import app
from info import API_HASH, API_ID
from pyrogram import filters, idle, Client


@app.on_message(filters.command("clonebot"))
async def clone(bot, msg):
    if len(msg.command == 1):
        return await msg.reply("Usage:\n\n /clonebot token")
    token = msg.command[1]
    text = await msg.reply("Cloning bot..")
    try:
        await text.edit("Booting Your Client")
        # change this Directry according to ur repo
        client = Client(":memory:",
                        API_ID,
                        API_HASH,
                        bot_token=token,
                        plugins={"root": "bot/clone_plugins"})
        await client.start()
        idle()
        user = await client.get_me()
        await text.edit(
            f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning."
        )
    except Exception as e:
        await msg.reply(f"**ERROR:** `{str(e)}`")