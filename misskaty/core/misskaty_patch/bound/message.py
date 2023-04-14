import io
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.sync import async_to_sync
from pyrogram import enums
from datetime import datetime
from asyncio import sleep as asleep, get_event_loop
from typing import Union, Optional

async def input_str(self) -> str:
    input_ = self.text
    if ' ' in input_ or '\n' in input_:
        return str(input_.split(maxsplit=1)[1].strip())
    return ''


async def del_in(self: Message, seconds: int, revoke: bool=True):
    """Delete message in x Seconds"""
    await asleep(seconds)
    return await self.delete(revoke=revoke)

async def reply(self: Message,
                text: str,
                del_in: int = -1,
                quote: Optional[bool] = None,
                parse_mode: Optional[enums.ParseMode] = None,
                disable_web_page_preview: Optional[bool] = None,
                disable_notification: Optional[bool] = None,
                reply_to_message_id: Optional[int] = None,
                schedule_date: Optional[datetime] = None,
                protect_content: Optional[bool] = None,
                reply_markup: InlineKeyboardMarkup = None) -> Union['Message', bool]:
        """\nExample:
                message.reply("hello")
        Parameters:
            text (``str``):
                Text of the message to be sent.
            del_in (``int``):
                Time in Seconds for delete that message.
            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.
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
        if reply_to_message_id is None:
            reply_to_message_id = self.id
        return await self.reply_text(text=text,
                                    del_in=del_in,
                                    parse_mode=parse_mode,
                                               disable_web_page_preview=disable_web_page_preview,
                                               disable_notification=disable_notification,
                                               reply_to_message_id=reply_to_message_id,
                                               schedule_date=schedule_date,
                                               protect_content=protect_content,
                                               reply_markup=reply_markup)


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

Message.input = input_str
Message.reply_text = reply
Message.reply_as_file = reply_as_file
Message.delete_in = del_in
async_to_sync(Message, 'delete_in')