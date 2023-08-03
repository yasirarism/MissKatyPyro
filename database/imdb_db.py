from database import dbname

imbd_db = dbname["imdb"]


async def is_imdbset(user_id: int) -> bool:
    user = await imbd_db.find_one({"user_id": user_id})
    return (True, user["lang"]) if user else (False, {})


async def add_imdbset(user_id: int, lang):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"lang": lang}}, upsert=True
    )


async def remove_imdbset(user_id: int):
    user = await imbd_db.find_one({"user_id": user_id})
    if user:
        return await imbd_db.delete_one({"user_id": user_id})
