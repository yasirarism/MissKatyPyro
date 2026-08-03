# Nightmode: daftar grup yang memiliki fitur nightmode aktif.
# Saat bot kena ChatWriteForbidden di grup tersebut, data grup dihapus + auto-leave.

from database import dbname

nightmodedb = dbname["nightmode"]
nightmode_cache = {}


async def is_nightmode_on(chat_id: int) -> bool:
    mode = nightmode_cache.get(chat_id)
    if mode is not None:
        return mode
    user = await nightmodedb.find_one({"chat_id": chat_id})
    nightmode_cache[chat_id] = bool(user)
    return bool(user)


async def nightmode_on(chat_id: int):
    nightmode_cache[chat_id] = True
    user = await nightmodedb.find_one({"chat_id": chat_id})
    if not user:
        await nightmodedb.insert_one({"chat_id": chat_id})


async def nightmode_off(chat_id: int):
    nightmode_cache[chat_id] = False
    user = await nightmodedb.find_one({"chat_id": chat_id})
    if user:
        await nightmodedb.delete_one({"chat_id": chat_id})
    nightmode_cache.pop(chat_id, None)


async def forget_chat(chat_id: int):
    """Hapus data nightmode grup (dipanggil saat auto-leave)."""
    nightmode_cache.pop(chat_id, None)
    await nightmodedb.delete_one({"chat_id": chat_id})