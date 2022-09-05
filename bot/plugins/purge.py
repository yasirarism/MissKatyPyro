"""Purge Messages
Syntax: .purge"""
from info import COMMAND_HANDLER
import asyncio
from bot import app
from pyrogram import filters, enums

__MODULE__ = "Admin"
__HELP__ = """
/purge - Delete many message in group.
/adminlist - Get adminlist in group.
/pin [reply to message] - Pin message in group.
"""

@app.on_message(filters.command(["purge"], COMMAND_HANDLER))
async def purge(client, message):
    """purge upto the replied message"""
    admin = await client.get_chat_member(message.chat.id, message.from_user.id)

    if admin.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply_text("This command only for admin..", quote=True)

    status_message = await message.reply_text("Processing..", quote=True)
    await message.delete()
    message_ids = []
    count_del_etion_s = 0

    if message.reply_to_message:
        for a_s_message_id in range(message.reply_to_message.id, message.id):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await client.delete_messages(chat_id=message.chat.id, message_ids=message_ids, revoke=True)
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await client.delete_messages(chat_id=message.chat.id, message_ids=message_ids, revoke=True)
            count_del_etion_s += len(message_ids)

    await status_message.edit_text(f"{count_del_etion_s} message deleted..")
    await asyncio.sleep(5)
    await status_message.delete()
