import asyncio
import datetime
import time

from pyrogram import filters
from pyrogram.types import Message

from database.users_chats_db import db
from misskaty import app
from misskaty.vars import SUDO
from utils import broadcast_messages


@app.on_message(filters.command("broadcast") & filters.user(SUDO) & filters.reply)
async def broadcast(_, ctx: Message):
    users = await db.get_all_users()
    b_msg = ctx.reply_to_message
    sts = await ctx.reply_msg("Broadcasting your messages...")
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0

    success = 0
    async for user in users:
        pti, sh = await broadcast_messages(int(user["id"]), b_msg)
        if pti:
            success += 1
        elif pti is False:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit_msg(
                f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}"
            )
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit_msg(
        f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}"
    )
