from database import dbname

greetingdb = dbname["greetings"]

async def is_welcome(chat_id: int) -> bool:
    greets = await greetingdb.find_one({"chat_id": chat_id})
    return bool(greets)

async def welcome_off(chat_id: int):
    wlc = await greetingdb.find_one({"chat_id": chat_id})
    if wlc:
        return await cleandb.delete_one({"chat_id": chat_id})

async def welcome_on(chat_id: int):
    wlc = await greetingdb.find_one({"chat_id": chat_id})
    if not wlc:
        return await greetingdb.insert_one({"chat_id": chat_id})

# todo other features for custom welcome here
