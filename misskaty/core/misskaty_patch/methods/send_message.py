import asyncio
from typing import Union

from pyrogram import Client


async def send_message(
    self, chat_id: Union[int, str], text: str, del_in: int = 0, *args, **kwargs
) -> Union["Message", bool]:
    """\nSend text messages.
    Example:
            @userge.send_message(chat_id=12345, text='test')
    Parameters:
        chat_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages)
            you can simply use "me" or "self".
            For a contact that exists in your Telegram address book
            you can use his phone number (str).
        text (``str``):
            Text of the message to be sent.
        del_in (``int``):
            Time in Seconds for delete that message.
        log (``bool`` | ``str``, *optional*):
            If ``True``, the message will be forwarded to the log channel.
            If ``str``, the logger name will be updated.
        parse_mode (:obj:`enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.
            Pass "markdown" or "md" to enable Markdown-style parsing only.
            Pass "html" to enable HTML-style parsing only.
            Pass None to completely disable style parsing.
        entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in message text,
            which can be specified instead of *parse_mode*.
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
        reply_markup (:obj:`InlineKeyboardMarkup` | :obj:`ReplyKeyboardMarkup`
        | :obj:`ReplyKeyboardRemove` | :obj:`ForceReply`, *optional*):
            Additional interface options. An object for an inline keyboard,
            custom reply keyboard, instructions to remove
            reply keyboard or to force a reply from the user.
    Returns:
        :obj:`Message`: On success, the sent text message or True is returned.
    """
    msg = await self.send_message(chat_id=chat_id, text=text, *args, **kwargs)
    if del_in == 0:
        return msg
    if del_in > 0:
        await asyncio.sleep(del_in)
        return bool(await msg.delete())


Client.send_msg = send_message
