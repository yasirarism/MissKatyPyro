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
