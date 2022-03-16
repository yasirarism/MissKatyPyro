from bot import app
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest

@app.on_chat_join_request(filters.chat(-1001686184174))
async def approve_join_chat(c: Client, m: ChatJoinRequest):
   if not m.from_user:
      return
   await c.send_message(m.from_user.id, "Makasih udah join..")
   await c.approve_chat_join_request(m.chat.id, m.from_user.id)
