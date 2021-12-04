from pyrogram import Client
from pyrogram.types import (
    Message
)
from typing import List

@Client.on_deleted_messages(filters.group)
async def on_del_mesgs(client, messages):
    for message in messages:
       await client.send_message(message)
