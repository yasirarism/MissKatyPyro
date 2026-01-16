import asyncio
import contextlib
from typing import Optional

from pyrogram import Client, filters as pyro_filters
from pyrogram.errors import ListenerTimeout
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message


async def listen(
    self: Client,
    chat_id: Optional[int],
    filters=None,
    timeout: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Message:
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    handler_group = -1

    async def _listener(client: Client, message: Message) -> None:
        if chat_id is not None and message.chat and message.chat.id != chat_id:
            return
        if user_id is not None:
            if not message.from_user or message.from_user.id != user_id:
                return
        if not future.done():
            future.set_result(message)

    handler_filters = filters or pyro_filters.all
    handler_filters &= pyro_filters.incoming
    if chat_id is not None:
        handler_filters &= pyro_filters.chat(chat_id)
    if user_id is not None:
        handler_filters &= pyro_filters.user(user_id)
    handler = MessageHandler(_listener, filters=handler_filters)
    self.add_handler(handler, group=handler_group)
    try:
        if timeout:
            return await asyncio.wait_for(future, timeout=timeout)
        return await future
    except asyncio.TimeoutError as exc:
        raise ListenerTimeout("Listener timeout.") from exc
    finally:
        with contextlib.suppress(Exception):
            self.remove_handler(handler, group=handler_group)


Client.listen = listen
