import html
import io
from asyncio import get_event_loop
from asyncio import sleep as asleep
from logging import getLogger
from typing import Union

from pyrogram.errors import (
    ChatAdminRequired,
    ChatSendPlainForbidden,
    ChatWriteForbidden,
    FloodWait,
    MessageAuthorRequired,
    MessageDeleteForbidden,
    MessageIdInvalid,
    MessageNotModified,
    MessageTooLong,
    TopicClosed,
)
from pyrogram.types import Message

LOGGER = getLogger("MissKaty")

Message.input = property(
    lambda m: m.text[m.text.find(m.command[0]) + len(m.command[0]) + 1 :]
    if len(m.command) > 1
    else None
)


async def reply_text(
    self: Message, text: str, as_raw: bool = False, del_in: int = 0, *args, **kwargs
) -> Union["Message", bool]:
    """\nExample:
            message.reply_msg("hello")
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
    try:
        if as_raw:
            msg = await self.reply_text(
                text=f"<code>{html.escape(text.html)}</code>", *args, **kwargs
            )
        else:
            msg = await self.reply_text(text=text, *args, **kwargs)
        if del_in == 0:
            return msg
        await asleep(del_in)
        return bool(await msg.delete_msg())
    except FloodWait as e:
        LOGGER.warning(f"Got floodwait in {self.chat.id} for {e.value}'s.")
        await asleep(e.value)
        return await reply_text(self, text, *args, **kwargs)
    except TopicClosed:
        return
    except (ChatWriteForbidden, ChatAdminRequired, ChatSendPlainForbidden):
        LOGGER.info(
            f"Leaving from {self.chat.title} [{self.chat.id}] because doesn't have enough permission."
        )
        return await self.chat.leave()


async def edit_text(
    self, text: str, del_in: int = 0, *args, **kwargs
) -> Union["Message", bool]:
    """\nExample:
            message.edit_msg("hello")
    Parameters:
        text (``str``):
            New text of the message.
        del_in (``int``):
            Time in Seconds for delete that message.
        parse_mode (:obj:`enums.ParseMode`, *optional*):
            By default, texts are parsed using
            both Markdown and HTML styles.
            You can combine both syntaxes together.
            Pass "markdown" or "md" to enable
            Markdown-style parsing only.
            Pass "html" to enable HTML-style parsing only.
            Pass None to completely disable style parsing.
        disable_web_page_preview (``bool``, *optional*):
            Disables link previews for links in this message.
        reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
            An InlineKeyboardMarkup object.
    Returns:
        On success, the edited
        :obj:`Message` or True is returned.
    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    try:
        msg = await self.edit_text(text, *args, **kwargs)
        if del_in == 0:
            return msg
        await asleep(del_in)
        return bool(await msg.delete_msg())
    except FloodWait as e:
        LOGGER.warning(f"Got floodwait in {self.chat.id} for {e.value}'s.")
        await asleep(e.value)
        return await edit_text(self, text, *args, **kwargs)
    except MessageNotModified:
        return False
    except (ChatWriteForbidden, ChatAdminRequired):
        LOGGER.info(
            f"Leaving from {self.chat.title} [{self.chat.id}] because doesn't have admin permission."
        )
        return await self.chat.leave()
    except (MessageAuthorRequired, MessageIdInvalid):
        return await reply_text(self, text=text, *args, **kwargs)


async def edit_or_send_as_file(
    self, text: str, del_in: int = 0, as_raw: bool = False, *args, **kwargs
) -> Union["Message", bool]:
    """\nThis will first try to message.edit.
    If it raises MessageTooLong error,
    run message.send_as_file.
    Example:
            message.edit_or_send_as_file("some huge text")
    Parameters:
        text (``str``):
            New text of the message.
        del_in (``int``):
            Time in Seconds for delete that message.
        log (``bool`` | ``str``, *optional*):
            If ``True``, the message will be forwarded
            to the log channel.
            If ``str``, the logger name will be updated.
        sudo (``bool``, *optional*):
            If ``True``, sudo users supported.
        as_raw (``bool``, *optional*):
            If ``False``, the message will be escaped with current parse mode.
            default to ``False``.
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
        reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
            An InlineKeyboardMarkup object.
        **kwargs (for message.send_as_file)
    Returns:
        On success, the edited
        :obj:`Message` or True is returned.
    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    text = html.escape(text.html) if as_raw else text
    try:
        msg = await edit_text(self, text=text, *args, **kwargs)
        if del_in == 0:
            return msg
        await asleep(del_in)
        return bool(await msg.delete_msg())
    except (MessageTooLong, OSError):
        return await reply_as_file(self, text=text, *args, **kwargs)


async def reply_or_send_as_file(
    self, text: str, as_raw: bool = False, del_in: int = 0, *args, **kwargs
) -> Union["Message", bool]:
    """\nThis will first try to message.reply.
    If it raise MessageTooLong error,
    run message.send_as_file.
    Example:
            message.reply_or_send_as_file("some huge text")
    Parameters:
        text (``str``):
            Text of the message to be sent.
        del_in (``int``):
            Time in Seconds for delete that message.
        quote (``bool``, *optional*):
            If ``True``, the message will be sent
            as a reply to this message.
            If *reply_to_message_id* is passed,
            this parameter will be ignored.
            Defaults to ``True`` in group chats
            and ``False`` in private chats.
        parse_mode (:obj:`enums.ParseMode`, *optional*):
            By default, texts are parsed using
            both Markdown and HTML styles.
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
            If the message is a reply, ID of the
            original message.
        reply_markup (:obj:`InlineKeyboardMarkup`
        | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove`
        | :obj:`ForceReply`, *optional*):
            Additional interface options. An object for an
            inline keyboard, custom reply keyboard,
            instructions to remove reply keyboard
            or to force a reply from the user.
        **kwargs (for message.send_as_file)
    Returns:
        On success, the sent Message or True is returned.
    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    text = html.escape(text.html) if as_raw else text
    try:
        return await reply_text(self, text=text, del_in=del_in, *args, **kwargs)
    except MessageTooLong:
        return await reply_as_file(self, text=text, **kwargs)


async def reply_as_file(
    self,
    text: str,
    filename: str = "output.txt",
    caption: str = "",
    delete_message: bool = True,
):
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
    return await self.reply_document(
        document=doc,
        caption=caption[:1024],
        disable_notification=True,
        reply_to_message_id=reply_to_id,
    )


async def delete(self, revoke: bool = True) -> bool:
    """\nThis will first try to delete and ignore
    it if it raises MessageDeleteForbidden
    Parameters:
        revoke (``bool``, *optional*):
            Deletes messages on both parts.
            This is only for private cloud chats and normal groups, messages on
            channels and supergroups are always revoked (i.e.: deleted for everyone).
            Defaults to True.
    Returns:
        True on success, False otherwise.
    """
    try:
        return bool(await self.delete(revoke=revoke))
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asleep(e.value)
        return await delete(self, revoke)
    except MessageDeleteForbidden:
        return False
    except Exception as e:
        LOGGER.warning(str(e))


Message.reply_msg = reply_text
Message.edit_msg = edit_text
Message.edit_or_send_as_file = edit_or_send_as_file
Message.reply_or_send_as_file = reply_or_send_as_file
Message.reply_as_file = reply_as_file
Message.delete_msg = delete
