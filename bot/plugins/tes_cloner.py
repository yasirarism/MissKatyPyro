from bot import app
from info import API_HASH, API_ID
from pyrogram import filters, idle, Client
from bot.utils.tools import get_random_string


@app.on_message(filters.command("clonebot"))
async def clone(client, message):
    if len(message.command) == 1:
        return await message.reply("Usage:\n\n /clonebot token")
    token = message.command[1]
    text = await message.reply("Cloning bot..")
    client_name = get_random_string(4)
    try:
        await text.edit("Booting Your Client")
        # change this Directry according to ur repo
        client_name = Client(":memory:",
                             API_ID,
                             API_HASH,
                             bot_token=token,
                             plugins={"root": "bot/clone_plugins"})
        await client_name.start()
        idle()
        user = await client_name.get_me()
        await text.edit(
            f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning."
        )
    except Exception as e:
        await message.reply(f"**ERROR:** `{str(e)}`")