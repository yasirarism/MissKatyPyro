from misskaty import app
from pyrogram import filters
from database.sangmata_db import *

# Check user that change first_name, last_name and usernaname
@app.on_message(
    filters.group & filters.chat(-1001580327675) & ~filters.bot & ~filters.via_bot,
    group=3,
)
async def cek_mataa(_, m):
    await m.reply("aaaa")
    if not await cek_userdata(m.from_user.id):
        return await add_userdata(m.from_user.id, m.from_user.username)
    username = await get_userdata(m.from_user.id)
    if username != m.from_user.username:
        await m.reply(f"{m.from_user.mention} mengganti username dari {username} menjadi {m.from_user.username}")
        await add_userdata(m.from_user.id, m.from_user.username)