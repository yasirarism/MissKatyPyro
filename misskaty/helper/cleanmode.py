
import asyncio
from datetime import datetime, timedelta

from pyrogram.errors import FloodWait

from database.afk_db import is_cleanmode_on

_ttl = timedelta(minutes=1)
_clean_interval = 30  # seconds between sweep cycles


async def put_cleanmode(chat_id, message_id):
    from misskaty import cleanmode

    cleanmode.setdefault(chat_id, [])
    cleanmode[chat_id].append(
        {"msg_id": message_id, "timer_after": datetime.now() + _ttl}
    )


async def auto_clean():
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
