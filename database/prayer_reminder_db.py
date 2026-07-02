from typing import Optional

from database import dbname
from misskaty.vars import TZ

prayer_reminderdb = dbname["prayerReminder"]
DEFAULT_CONFIG = {
    "_id": "default",
    "enabled": False,
    "city_id": "57aeee35c98205091e18d1140e9f38cf",
    "city_name": "KOTA SURAKARTA",
    "timezone": TZ,
    "chat_id": None,
    "thread_id": None,
    "last_sent": None,
}


async def get_prayer_config() -> dict:
    config = await prayer_reminderdb.find_one({"_id": "default"})
    if not config:
        return DEFAULT_CONFIG.copy()
    data = DEFAULT_CONFIG.copy()
    data.update(config)
    return data


async def update_prayer_config(**kwargs) -> dict:
    await prayer_reminderdb.update_one(
        {"_id": "default"}, {"$set": kwargs}, upsert=True
    )
    return await get_prayer_config()


async def set_prayer_enabled(enabled: bool) -> dict:
    return await update_prayer_config(enabled=enabled)


async def set_prayer_target(chat_id: int, thread_id: Optional[int] = None) -> dict:
    return await update_prayer_config(chat_id=chat_id, thread_id=thread_id)


async def set_prayer_city(city_id: str, city_name: str) -> dict:
    return await update_prayer_config(city_id=city_id, city_name=city_name)


async def set_prayer_last_sent(last_sent: str) -> dict:
    return await update_prayer_config(last_sent=last_sent)
