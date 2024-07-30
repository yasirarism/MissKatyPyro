from database import dbname

greetingdb = dbname["greetings"]


async def is_welcome(chat_id: int) -> bool:
    return bool(await greetingdb.find_one({"chat_id": chat_id}))


async def toggle_welcome(chat_id: int):
    if await is_welcome(chat_id):
        await greetingdb.delete_one({"chat_id": chat_id})
        return False
    else:
        await greetingdb.insert_one({"chat_id": chat_id})
        return True


# todo other features for custom welcome here
