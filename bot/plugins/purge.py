"""Purge Messages
Syntax: .purge"""
from bot import app
from info import COMMAND_HANDLER
import asyncio
from pyrogram import filters


@app.on_message(filters.command(["purge","purge@MissKatyRoBot"], COMMAND_HANDLER))
async def purge(_, message):
    """ purge upto the replied message """
    if message.chat.type not in (("supergroup", "channel")):
        # https://t.me/c/1312712379/84174
        return

    is_admin = await app.get_chat_member(message.chat.id, message.from_user.id)

    if user.status in ['administrator','creator']:
        return await message.reply_text("Command ini hanya untuk admin..", quote=True)

    status_message = await message.reply_text("Sedang Memproses..", quote=True)
    await message.delete()
    message_ids = []
    count_del_etion_s = 0

    if message.reply_to_message:
        for a_s_message_id in range(
            message.reply_to_message.message_id,
            message.message_id
        ):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_del_etion_s += len(message_ids)

    await status_message.edit_text(
        f"{count_del_etion_s} Pesan dihapus.."
    )
    await asyncio.sleep(5)
    await status_message.delete()
