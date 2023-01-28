from misskaty import app
from pyrogram import filters
from database.sangmata_db import *

# Check user that change first_name, last_name and usernaname
@app.on_message(
    filters.group & filters.chat(-1001580327675) & ~filters.bot & ~filters.via_bot,
    group=3,
)
async def cek_mataa(_, m):
    if not await cek_userdata(m.from_user.id):
        return await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    username, first_name, last_name = await get_userdata(m.from_user.id)
    msg == ""
    if username != m.from_user.username or first_name != m.from_user.first_name or last_name != m.from_user.last_name:
        msg += "👀 <b>Mata MissKaty</b>\n\n"
    if username != m.from_user.username:
        msg += f"{m.from_user.mention} mengganti username dari {username} menjadi {m.from_user.username}.\n"
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if first_name != m.from_user.first_name:
        msg += f"{m.from_user.mention} mengganti username dari {username} menjadi {m.from_user.username}.\n"
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if last_name != m.from_user.last_name:
        msg += f"{m.from_user.mention} mengganti username dari {username} menjadi {m.from_user.username}."
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    await m.reply(msg)