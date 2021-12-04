from pyrogram import Client
from pyrogram.types import (
    Message
)
from typing import List

@Client.on_deleted_messages()
async def on_del_mesgs(client: Client, messages: List[Message]):
    for message in messages:
       await client.send_message(message.message_id)
