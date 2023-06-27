#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiAFKBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiAFKBot/blob/master/LICENSE >
#
# All rights reserved.
#

from database import dbname

usersdb = dbname["users"]
cleandb = dbname["cleanmode"]
cleanmode = {}


async def is_cleanmode_on(chat_id: int) -> bool:
    mode = cleanmode.get(chat_id)
    if not mode:
        user = await cleandb.find_one({"chat_id": chat_id})
        if not user:
            cleanmode[chat_id] = True
            return True
        cleanmode[chat_id] = False
        return False
    return mode


async def cleanmode_on(chat_id: int):
    cleanmode[chat_id] = True
    user = await cleandb.find_one({"chat_id": chat_id})
    if user:
        return await cleandb.delete_one({"chat_id": chat_id})


async def cleanmode_off(chat_id: int):
    cleanmode[chat_id] = False
    user = await cleandb.find_one({"chat_id": chat_id})
    if not user:
        return await cleandb.insert_one({"chat_id": chat_id})


async def is_afk(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    return (True, user["reason"]) if user else (False, {})


async def add_afk(user_id: int, mode):
    await usersdb.update_one(
        {"user_id": user_id}, {"$set": {"reason": mode}}, upsert=True
    )


async def remove_afk(user_id: int):
    user = await usersdb.find_one({"user_id": user_id})
    if user:
        return await usersdb.delete_one({"user_id": user_id})


async def get_afk_users() -> list:
    users = usersdb.find({"user_id": {"$gt": 0}})
    return list(await users.to_list(length=1000000000)) if users else []
