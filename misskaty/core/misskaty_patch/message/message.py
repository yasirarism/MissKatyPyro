from pyrogram.types import Message
from pyrogram.sync import async_to_sync
from asyncio import sleep as asleep

Message.input = property(
    lambda m: m.text[m.text.find(m.command[0]) + len(m.command[0]) + 1:] 
    if len(m.command) > 1 else None
)

async def del_in(self: Message, seconds: int, revoke: bool=True):
    """Delete message in x Seconds"""
    await asleep(seconds)
    return await self.delete(revoke=revoke)
Message.delete_in = del_in
async_to_sync(Message, 'delete_in')