from database import dbname

imbd_db = dbname["imdb"]


async def is_imdbset(user_id: int) -> bool:
    user = await imbd_db.find_one({"user_id": user_id})
    lang = user.get("lang") if user else None
    return (bool(lang), lang)


async def add_imdbset(user_id: int, lang):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"lang": lang}}, upsert=True
    )


async def remove_imdbset(user_id: int):
    await imbd_db.update_one({"user_id": user_id}, {"$unset": {"lang": ""}})


async def get_imdb_template(user_id: int) -> str:
    user = await imbd_db.find_one({"user_id": user_id})
    return user.get("template", "") if user else ""


async def set_imdb_template(user_id: int, template: str):
    await imbd_db.update_one(
        {"user_id": user_id}, {"$set": {"template": template}}, upsert=True
    )


async def clear_imdb_template(user_id: int):
    await imbd_db.update_one({"user_id": user_id}, {"$unset": {"template": ""}})
