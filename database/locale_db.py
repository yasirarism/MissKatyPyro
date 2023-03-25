from pyrogram.enums import ChatType
from typing import Iterable
from database import dbname

localesdb = dbname.locale # DB for localization

group_types: Iterable[ChatType] = (ChatType.GROUP, ChatType.SUPERGROUP)

async def set_db_lang(chat_id: int, chat_type: str, lang_code: str):
    await localesdb.update_one({"chat_id": chat_id}, {"$set": {"lang": lang_code, "chat_type": chat_type}}, upsert=True)


async def get_db_lang(chat_id: int, chat_type: str) -> str:
    ul = await localesdb.find_one({"chat_id": chat_id})
    return ul["lang"] if ul else {}