import io
from pyrogram.types import Message
from pyrogram.sync import async_to_sync
from asyncio import sleep as asleep, get_event_loop
from typing import Union
from misskaty import app, user
from ..types.send_as_file import send_as_file

Message.input = property(
    lambda m: m.text[m.text.find(m.command[0]) + len(m.command[0]) + 1:] 
    if len(m.command) > 1 else None
)

async def del_in(self: Message, seconds: int, revoke: bool=True):
    """Delete message in x Seconds"""
    await asleep(seconds)
    return await self.delete(revoke=revoke)

async def reply_as_file(self, client: Union['app', 'user'], text: str, filename: str = "output.txt", caption: str = '', delete_message: bool = True):
        """\nYou can send large outputs as file
        Example:
            message.reply_as_file(text="hello")
        Parameters:
            text (``str``):
                Text of the message to be sent.
            filename (``str``, *optional*):
                file_name for output file.
            caption (``str``, *optional*):
                caption for output file.
            delete_message (``bool``, *optional*):
                If ``True``, the message will be deleted
                after sending the file.
        Returns:
            On success, the sent Message is returned.
        """
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
Message.delete_in = del_in
async_to_sync(Message, 'delete_in')