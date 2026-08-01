from typing import Optional

from database import dbname
from misskaty.vars import TZ

prayer_reminderdb = dbname["prayerReminder"]
DEFAULT_CONFIG = {
    "enabled": False,
    "city_id": "57aeee35c98205091e18d1140e9f38cf",
    "city_name": "KOTA SURAKARTA",
    "timezone": TZ,
    "chat_id": None,
    "thread_id": None,
    "last_sent": None,
    "schedule_date": None,
    "schedule": None,
}


def _default_config(chat_id: int) -> dict:
    config = DEFAULT_CONFIG.copy()
    config.update({"_id": str(chat_id), "chat_id": chat_id})
    return config


async def get_prayer_config(chat_id: int) -> dict:
    config = await prayer_reminderdb.find_one({"_id": str(chat_id)})
    if not config:
        return _default_config(chat_id)
    data = _default_config(chat_id)
    data.update(config)
    return data


async def get_enabled_prayer_configs() -> list[dict]:
    configs = []
    async for config in prayer_reminderdb.find({"enabled": True, "chat_id": {"$ne": None}}):
        data = _default_config(config["chat_id"])
        data.update(config)
        configs.append(data)
    return configs


async def update_prayer_config(chat_id: int, **kwargs) -> dict:
    kwargs["chat_id"] = chat_id
    await prayer_reminderdb.update_one(
        {"_id": str(chat_id)}, {"$set": kwargs}, upsert=True
    )
    return await get_prayer_config(chat_id)


async def set_prayer_enabled(chat_id: int, enabled: bool) -> dict:
    return await update_prayer_config(chat_id, enabled=enabled)


async def set_prayer_target(chat_id: int, thread_id: Optional[int] = None) -> dict:
    return await update_prayer_config(chat_id, thread_id=thread_id)


async def set_prayer_city(chat_id: int, city_id: str, city_name: str) -> dict:
    return await update_prayer_config(
        chat_id, city_id=city_id, city_name=city_name, schedule_date=None, schedule=None
    )


async def set_prayer_last_sent(chat_id: int, last_sent: str) -> dict:
    return await update_prayer_config(chat_id, last_sent=last_sent)


async def set_prayer_schedule(chat_id: int, schedule_date: str, schedule: dict) -> dict:
    return await update_prayer_config(
        chat_id, schedule_date=schedule_date, schedule=schedule
    )
