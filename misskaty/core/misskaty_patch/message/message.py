import io
from pyrogram.types import Message
from pyrogram.sync import async_to_sync
from asyncio import sleep as asleep, get_event_loop

Message.input = property(
    lambda m: m.text[m.text.find(m.command[0]) + len(m.command[0]) + 1:] 
    if len(m.command) > 1 else None
)

async def del_in(self: Message, seconds: int, revoke: bool=True):
    """Delete message in x Seconds"""
    await asleep(seconds)
    return await self.delete(revoke=revoke)
Message.delete_in = del_in

async def reply_as_file(self: Message, text: str, filename: str = "output.txt", caption: str = '', delete_message: bool = True):
    reply_to_id = self.reply_to_message.id if self.reply_to_message else self.id
    if delete_message:
        get_event_loop().create_task(self.delete())
    doc = io.BytesIO(text.encode())
    doc.name = filename
    return await self.reply_document(document=doc,
                                    caption=caption[:1024],
                                    disable_notification=True,
                                    reply_to_message_id=reply_to_id)
Message.reply_as_file = reply_as_file
async_to_sync(Message, 'delete_in')