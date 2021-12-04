from pyrogram import Client, filters
from bot import app
from pyrogram.types import (
    Message
)
from typing import List

@app.on_deleted_messages(filters.group)
async def deleted(_: Client, messages: List[Message]):
    for message in messages:
       await app.send_message(message.chat.id, message)
