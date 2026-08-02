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
    # Jangan lanjut — biarkan handler asli diproses juga
