from pyrogram import Client, filters
from pyrogram.types import (
    Message
)
from typing import List

@Client.on_deleted_messages(filters.group)
async def del_msg(client: Client, messages: List[Message]):
    for msg in messages:
       await client.send_message(msg.chat.id, msg.text)
