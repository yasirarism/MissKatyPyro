from pyrogram import Client
from pyrogram.types import filters


@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hey! I'm cloned by @YasirArisM")