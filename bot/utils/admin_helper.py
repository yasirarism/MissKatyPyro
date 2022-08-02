import imp
from pyrogram import enums
from bot import app


async def is_admin(group_id: int, user_id: int):
    try:
        user_data = await app.get_chat_member(group_id, user_id)
        return user_data.status in [
            enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER
        ]
    except:
        # print('Not admin')
        return False
