import io
from typing import Optional, Union

from pyrogram import Client
from pyrogram.types import Message


async def send_as_file(
    self,
    chat_id: Union[int, str],
    text: str,
    filename: str = "output.txt",
    caption: str = "",
    log: Union[bool, str] = False,
    reply_to_message_id: Optional[int] = None,
) -> "Message":
    """\nYou can send large outputs as file
    Example:
            @userge.send_as_file(chat_id=12345, text="hello")
    Parameters:
        chat_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages)
            you can simply use "me" or "self".
            For a contact that exists in your Telegram address book
            you can use his phone number (str).
        text (``str``):
            Text of the message to be sent.
        filename (``str``, *optional*):
            file_name for output file.
        caption (``str``, *optional*):
            caption for output file.
        log (``bool`` | ``str``, *optional*):
            If ``True``, the message will be forwarded
            to the log channel.
            If ``str``, the logger name will be updated.
        reply_to_message_id (``int``, *optional*):
            If the message is a reply, ID of the original message.
    Returns:
        On success, the sent Message is returned.
    """
    doc = io.BytesIO(text.encode())
    doc.name = filename

    return await self.send_document(
        chat_id=chat_id,
        document=doc,
        caption=caption[:1024],
        disable_notification=True,
        reply_to_message_id=reply_to_message_id,
    )


Client.send_as_file = send_as_file
