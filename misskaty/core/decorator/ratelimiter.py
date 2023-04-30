from cachetools import TTLCache
from functools import wraps
from ..ratelimiter_func import RateLimiter
from typing import Callable, Union
from pyrogram import Client
from pyrogram.types import CallbackQuery, Message
from pyrogram.errors import QueryIdInvalid

ratelimit = RateLimiter()
# storing spammy user in cache for 1minute before allowing them to use commands again.
warned_users = TTLCache(maxsize=128, ttl=60)
warning_message = "Spam detected! ignoring your all requests for few minutes."


def ratelimiter(func: Callable) -> Callable:
    """
    Restricts user's from spamming commands or pressing buttons multiple times
    using leaky bucket algorithm and pyrate_limiter.
    """

    @wraps(func)
    async def decorator(client: Client, update: Union[Message, CallbackQuery]):
        userid = update.from_user.id if update.from_user else update.sender_chat.id
        is_limited = await ratelimit.acquire(userid)

        if is_limited and userid not in warned_users:
            if isinstance(update, Message):
                await update.reply_text(warning_message)
                warned_users[userid] = 1
                return

            elif isinstance(update, CallbackQuery):
                try:
                    await update.answer(warning_message, show_alert=True)
                except QueryIdInvalid:
                    warned_users[userid] = 1
                    return
                warned_users[userid] = 1
                return

        elif is_limited and userid in warned_users:
            pass
        else:
            return await func(client, update)

    return decorator
