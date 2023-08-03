from database import dbname

matadb = dbname["sangmata"]


# Get Data User
async def cek_userdata(user_id: int) -> bool:
    user = await matadb.find_one({"user_id": user_id})
    return bool(user)


async def get_userdata(user_id: int) -> bool:
    user = await matadb.find_one({"user_id": user_id})
    return user["username"], user["first_name"], user["last_name"]


async def add_userdata(user_id: int, username, first_name, last_name):
    await matadb.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        },
        upsert=True,
    )


# Enable Mata MissKaty in Selected Chat
async def is_sangmata_on(chat_id: int) -> bool:
    chat = await matadb.find_one({"chat_id_toggle": chat_id})
    return bool(chat)


async def sangmata_on(chat_id: int) -> bool:
    await matadb.insert_one({"chat_id_toggle": chat_id})


async def sangmata_off(chat_id: int):
    await matadb.delete_one({"chat_id_toggle": chat_id})
