from database import dbname

matadb = dbname.sangmata

async def cek_userdata(user_id: int) -> bool:
    user = await matadb.find_one({"user_id": user_id})
    return True if user else False

async def get_userdata(user_id: int) -> bool:
    user = await matadb.find_one({"user_id": user_id})
    return user["username"], user["first_name"], user["last_name"]

async def add_userdata(user_id: int, username, first_name, last_name):
    await matadb.update_one({"user_id": user_id}, {"$set": {"username": username, "first_name": first_name, "last_name": last_name}}, upsert=True)