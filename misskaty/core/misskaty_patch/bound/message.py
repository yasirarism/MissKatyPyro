import io
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram import enums
from pyrogram.sync import async_to_sync
from datetime import datetime
from asyncio import sleep as asleep, get_event_loop
from typing import Union, Optional

Message.input = property(
    lambda m: m.text[m.text.find(m.command[0]) + len(m.command[0]) + 1:] 
    if len(m.command) > 1 else None
)

async def reply_text(self: Message,
                text: str,
                del_in: int = -1,
                *args,
                **kwargs) -> Union['Message', bool]:
        """\nExample:
                message.reply("hello")
        Parameters:
            text (``str``):
                Text of the message to be sent.
            del_in (``int``):
                Time in Seconds for delete that message.
            quote (``bool``, *optional*):
                If ``True``, the message will be sent as
                a reply to this message.
                If *reply_to_message_id* is passed,
                this parameter will be ignored.
                Defaults to ``True`` in group chats
                and ``False`` in private chats.
            parse_mode (:obj:`enums.ParseMode`, *optional*):
                By default, texts are parsed using both
                Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.
            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.
            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.
            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.
            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent. Unix time.
            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.
            reply_markup (:obj:`InlineKeyboardMarkup`
            | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove`
            | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard,
                custom reply keyboard,
                instructions to remove reply keyboard or to
                force a reply from the user.
        Returns:
            On success, the sent Message or True is returned.
        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        msg = await self.reply_text(text=text,
                                    *args,
                                    **kwargs)
        if del_in == 0:
            return True
        await asleep(del_in)
        return bool(await msg.delete())


async def reply_as_file(self, text: str, filename: str = "output.txt", caption: str = '', delete_message: bool = True):
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

Message.reply_msg = reply_text
Message.reply_as_file = reply_as_file