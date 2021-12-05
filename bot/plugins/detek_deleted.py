from pyrogram import Client, filters
from pyrogram.types import (
    Message
)
from typing import List
from bot import user, app

@user.on_deleted_messages()
async def del_msg(client, message):
    #for msg in messages:
    await app.send_message(617426792, message)
