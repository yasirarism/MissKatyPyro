import pytz
from datetime import datetime
from misskaty.vars import SUDO
from database import dbname


fedsdb = dbname["federation"]


def get_fed_info(fed_id):
    get = fedsdb.find_one({"fed_id": str(fed_id)})
    return False if get is None else get


async def get_fed_id(chat_id):
    get = await fedsdb.find_one({"chat_ids.chat_id": int(chat_id)})

    if get is None:
        return False
    return next(
        (
            get["fed_id"]
            for chat_info in get.get("chat_ids", [])
            if chat_info["chat_id"] == int(chat_id)
        ),
        False,
    )


async def get_feds_by_owner(owner_id):
    cursor = fedsdb.find({"owner_id": owner_id})
    feds = await cursor.to_list(length=None)
    if not feds:
        return False
    return [
        {"fed_id": fed["fed_id"], "fed_name": fed["fed_name"]} for fed in feds
    ]


async def transfer_owner(fed_id, current_owner_id, new_owner_id):
    if await is_user_fed_owner(fed_id, current_owner_id):
        await fedsdb.update_one(
            {"fed_id": fed_id, "owner_id": current_owner_id},
            {"$set": {"owner_id": new_owner_id}},
        )
        return True
    else:
        return False


async def set_log_chat(fed_id, log_group_id: int):
    await fedsdb.update_one(
        {"fed_id": fed_id}, {"$set": {"log_group_id": log_group_id}}
    )
    return


async def get_fed_name(chat_id):
    get = await fedsdb.find_one(int(chat_id))
    return False if get is None else get["fed_name"]


async def is_user_fed_owner(fed_id, user_id: int):
    getfed = await get_fed_info(fed_id)
    if not getfed:
        return False
    owner_id = getfed["owner_id"]
    return user_id == owner_id or user_id not in SUDO


async def search_fed_by_id(fed_id):
    get = await fedsdb.find_one({"fed_id": str(fed_id)})

    return get if get is not None else False


def chat_join_fed(fed_id, chat_name, chat_id):
    return fedsdb.update_one(
        {"fed_id": fed_id},
        {"$push": {"chat_ids": {"chat_id": int(chat_id), "chat_name": chat_name}}},
    )


async def chat_leave_fed(chat_id):
    result = await fedsdb.update_one(
        {"chat_ids.chat_id": int(chat_id)},
        {"$pull": {"chat_ids": {"chat_id": int(chat_id)}}},
    )
    return result.modified_count > 0


async def user_join_fed(fed_id, user_id):
    result = await fedsdb.update_one(
        {"fed_id": fed_id}, {"$addToSet": {"fadmins": int(user_id)}}, upsert=True
    )
    return result.modified_count > 0


async def user_demote_fed(fed_id, user_id):
    result = await fedsdb.update_one(
        {"fed_id": fed_id}, {"$pull": {"fadmins": int(user_id)}}
    )
    return result.modified_count > 0


async def search_user_in_fed(fed_id, user_id):
    getfed = await search_fed_by_id(fed_id)
    return False if getfed is None else user_id in getfed["fadmins"]


async def chat_id_and_names_in_fed(fed_id):
    getfed = await search_fed_by_id(fed_id)

    if getfed is None or "chat_ids" not in getfed:
        return [], []

    chat_ids = [chat["chat_id"] for chat in getfed["chat_ids"]]
    chat_names = [chat["chat_name"] for chat in getfed["chat_ids"]]
    return chat_ids, chat_names


async def add_fban_user(fed_id, user_id, reason):
    current_date = datetime.now(pytz.timezone("Asia/Jakarta")).strftime(
        "%Y-%m-%d %H:%M"
    )
    await fedsdb.update_one(
        {"fed_id": fed_id},
        {
            "$push": {
                "banned_users": {
                    "user_id": int(user_id),
                    "reason": reason,
                    "date": current_date,
                }
            }
        },
        upsert=True,
    )


async def remove_fban_user(fed_id, user_id):
    await fedsdb.update_one(
        {"fed_id": fed_id}, {"$pull": {"banned_users": {"user_id": int(user_id)}}}
    )


async def check_banned_user(fed_id, user_id):
    result = await fedsdb.find_one({"fed_id": fed_id, "banned_users.user_id": user_id})
    if result and "banned_users" in result:
        for user in result["banned_users"]:
            if user.get("user_id") == user_id:
                return {"reason": user.get("reason"), "date": user.get("date")}

    return False
