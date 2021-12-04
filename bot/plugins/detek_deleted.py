from pyrogram import Client, filters
from pyrogram.types import (
    Message
)
from typing import List

@Client.on_deleted_messages(filters.group)
async def deleted(client: Client, messages: List[Message]):
    tmp = "".join(msg.message_id for msg in msgs.messages)
    await client.send_message(messages.chat.id, temp)
