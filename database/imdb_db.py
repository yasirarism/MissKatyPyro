from database import dbname

imbd_db = dbname["imdb"]


async def is_imdbset(user_id: int) -> bool:
    user = await imbd_db.find_one({"user_id": user_id})
    if not user or "lang" not in user:
        return False, {}
    return True, user["lang"]


async def add_imdbset(user_id: int, lang):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"lang": lang}}, upsert=True
    )


async def remove_imdbset(user_id: int):
    user = await imbd_db.find_one({"user_id": user_id})
    if user:
        return await imbd_db.delete_one({"user_id": user_id})


async def get_imdb_template(user_id: int):
    user = await imbd_db.find_one({"user_id": user_id})
    return user.get("template") if user else None


async def set_imdb_template(user_id: int, template: str):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"template": template}}, upsert=True
    )


async def remove_imdb_template(user_id: int):
    await imbd_db.update_one({"user_id": user_id}, {"$unset": {"template": ""}})


async def get_imdb_layout(user_id: int) -> bool:
    user = await imbd_db.find_one({"user_id": user_id})
    if not user or "layout_enabled" not in user:
        return True
    return bool(user["layout_enabled"])


async def set_imdb_layout(user_id: int, enabled: bool):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"layout_enabled": enabled}}, upsert=True
    )


async def get_imdb_layout_fields(user_id: int):
    user = await imbd_db.find_one({"user_id": user_id})
    return user.get("layout_fields") if user else None


async def set_imdb_layout_fields(user_id: int, fields):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"layout_fields": fields}}, upsert=True
    )


async def reset_imdb_layout_fields(user_id: int):
    await imbd_db.update_one({"user_id": user_id}, {"$unset": {"layout_fields": ""}})


async def get_imdb_by(user_id: int):
    user = await imbd_db.find_one({"user_id": user_id})
    return user.get("imdb_by") if user else None


async def set_imdb_by(user_id: int, value: str):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"imdb_by": value}}, upsert=True
    )


async def remove_imdb_by(user_id: int):
    await imbd_db.update_one({"user_id": user_id}, {"$unset": {"imdb_by": ""}})
