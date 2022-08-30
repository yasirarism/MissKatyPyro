from pyrogram import Client
from pyrogram.types import *
from pyrogram import filters


@Client.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply("Hey! I'm cloned by @YasirArisM")