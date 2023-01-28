from database import dbname

matadb = dbname.sangmata

async def cek_userdata(user_id: int) -> bool:
    user = await matadb.find_one({"user_id": user_id})
    return True if user else False

async def get_userdata(user_id: int) -> bool:
    user = await matadb.find_one({"user_id": user_id})
    return user["username"]

async def add_userdata(user_id: int, username):
    await matadb.update_one({"user_id": user_id}, {"$set": {"username": username}}, upsert=True)