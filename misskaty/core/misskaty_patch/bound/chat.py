from typing import Optional

from pyrogram import filters as pyro_filters
from pyrogram.types import Chat, Message


async def ask(
    self: Chat,
    text: str,
    filters=None,
    timeout: Optional[int] = None,
    user_id: Optional[int] = None,
    *args,
    **kwargs,
) -> Message:
    await self._client.send_message(self.id, text, *args, **kwargs)
    return await self._client.listen(
        chat_id=self.id,
        filters=filters or pyro_filters.all,
        timeout=timeout,
        user_id=user_id,
    )


Chat.ask = ask
