"""Clean-mode helpers: track bot messages in chats and auto-delete them
after a short TTL so group chats stay tidy."""

import asyncio
from datetime import datetime, timedelta

from pyrogram.errors import FloodWait

from database.afk_db import is_cleanmode_on

_ttl = timedelta(minutes=1)
_clean_interval = 30  # seconds between sweep cycles


async def put_cleanmode(chat_id, message_id):
    """Register ``message_id`` to be auto-deleted from ``chat_id`` after TTL."""
    from misskaty import cleanmode

    cleanmode.setdefault(chat_id, [])
    cleanmode[chat_id].append(
        {"msg_id": message_id, "timer_after": datetime.now() + _ttl}
    )


async def auto_clean():
    """Background sweeper that deletes expired clean-mode messages.

    Runs every ``_clean_interval`` seconds. Per sweep it:
      * iterates over a snapshot of the chat ids (safe against concurrent
        ``put_cleanmode`` calls),
      * only touches chats that actually have expired messages,
      * deletes expired ids with a single ``delete_messages`` call per chat,
      * prunes already-processed entries so the in-memory dict cannot grow
        unboundedly.
    """
    from misskaty import app, cleanmode

    while True:
        await asyncio.sleep(_clean_interval)
        now = datetime.now()
        for chat_id in list(cleanmode):
            pending = cleanmode.get(chat_id)
            if not pending:
                cleanmode.pop(chat_id, None)
                continue

            expired = [m["msg_id"] for m in pending if m["timer_after"] <= now]
            if not expired:
                continue

            try:
                if not await is_cleanmode_on(chat_id):
                    continue
                await app.delete_messages(chat_id, expired)
                cleanmode[chat_id] = [
                    m for m in pending if m["timer_after"] > now
                ]
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue
