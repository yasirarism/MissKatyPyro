"""Debug sementara: catat semua callback query yang masuk ke bot."""
import logging

from pyrogram import filters

from misskaty import app

LOGGER = logging.getLogger("MissKaty")


@app.on_callback_query(filters.create(lambda _, __, q: True), group=-1)
async def debug_all_callbacks(_, cq):
    LOGGER.warning(
        f"[CATCHALL] callback data={cq.data!r} user={cq.from_user.id} chat={cq.message.chat.id}"
    )


# Handler duplikat dengan regex yang SAMA persis dengan media_extractor
@app.on_callback_query(filters.regex(r"^streamextract#"))
async def debug_streamextract_dup(_, cq):
    LOGGER.warning(f"[DUP-STREAMEXTRACT] callback data={cq.data!r}")


# Dump semua handler callback yang terdaftar saat plugin di-load
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

async def _dump_handlers():
    try:
        groups = app.dispatcher.groups
        lines = []
        for gid in sorted(groups.keys()):
            for handler in groups[gid]:
                if isinstance(handler, CallbackQueryHandler):
                    fs = repr(getattr(handler, "filters", None))
                    lines.append(f"CB g{gid}: {fs[:110]}")
                elif isinstance(handler, MessageHandler):
                    lines.append(f"MSG g{gid}")
        LOGGER.warning("[DUMP] callback handlers terdaftar:\n" + "\n".join(lines))
    except Exception as e:
        LOGGER.warning(f"[DUMP] gagal: {e}")

import asyncio
asyncio.get_event_loop().create_task(_dump_handlers())
