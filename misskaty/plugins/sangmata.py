from pyrogram import filters

from database.sangmata_db import *
from misskaty import app
from misskaty.core.decorator.permissions import adminsOnly
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.message_utils import kirimPesan
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "SangMata"
__HELP__ = """"
This feature inspired from SangMata Bot. I'm created simple detection to check user data include username, first_name, and last_name.
/sangmata_set [on/off] - Enable/disable sangmata in groups.
"""


# Check user that change first_name, last_name and usernaname
@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=3,
)
async def cek_mataa(_, m):
    if m.sender_chat or not await is_sangmata_on(m.chat.id):
        return
    if not await cek_userdata(m.from_user.id):
        return await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    username, first_name, last_name = await get_userdata(m.from_user.id)
    msg = ""
    if username != m.from_user.username or first_name != m.from_user.first_name or last_name != m.from_user.last_name:
        msg += "👀 <b>Mata MissKaty</b>\n\n"
    if username != m.from_user.username:
        username = "No Username" if not username else username
        msg += f"{m.from_user.mention} [<code>{m.from_user.id}</code>] changed username.\n"
        msg += f"From {username} ➡️ @{m.from_user.username}.\n"
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if first_name != m.from_user.first_name:
        msg += f"{m.from_user.mention} [<code>{m.from_user.id}</code>] changed first_name.\n"
        msg += f"From {first_name} ➡️ {m.from_user.first_name}.\n"
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if last_name != m.from_user.last_name:
        username = "No Lastname" if not username else username
        msg += f"{m.from_user.mention} [<code>{m.from_user.id}</code>] changed last_name.\n"
        msg += f"From {last_name} ➡️ {m.from_user.last_name}."
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if msg != "":
        await kirimPesan(m, msg, quote=True)


@app.on_message(filters.group & filters.command("sangmata_set", COMMAND_HANDLER) & ~filters.bot & ~filters.via_bot)
@adminsOnly("can_change_info")
@ratelimiter
async def set_mataa(_, m):
    if len(m.command) == 1:
        return await kirimPesan(m, f"Use <code>/{m.command[0]} on</code>, to enable sangmata. If you want disable, you can use off parameter.")
    if m.command[1] == "on":
        cekset = await is_sangmata_on(m.chat.id)
        if cekset:
            await kirimPesan(m, "SangMata already enabled in your groups.")
        else:
            await sangmata_on(m.chat.id)
            await kirimPesan(m, "Sangmata enabled in your groups.")
    elif m.command[1] == "off":
        cekset = await is_sangmata_on(m.chat.id)
        if not cekset:
            await kirimPesan(m, "SangMata already disabled in your groups.")
        else:
            await sangmata_off(m.chat.id)
            await kirimPesan(m, "Sangmata has been disabled in your groups.")
    else:
        await kirimPesan(m, "Unknown parameter, use only on/off parameter.")
