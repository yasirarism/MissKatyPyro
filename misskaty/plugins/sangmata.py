from pyrogram import filters

from database.sangmata_db import *
from misskaty import app
from misskaty.core.decorator.permissions import adminsOnly
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.message_utils import kirimPesan
from misskaty.helper.localization import use_chat_lang
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
@use_chat_lang()
async def cek_mataa(_, m, strings):
    if m.sender_chat or not await is_sangmata_on(m.chat.id):
        return
    if not await cek_userdata(m.from_user.id):
        return await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    usernamebefore, first_name, lastname_before = await get_userdata(m.from_user.id)
    msg = ""
    if usernamebefore != m.from_user.username or first_name != m.from_user.first_name or lastname_before != m.from_user.last_name:
        msg += f"👀 <b>Mata MissKaty</b>\n\n🌞 User: {m.from_user.mention} [<code>{m.from_user.id}</code>]\n"
    if usernamebefore != m.from_user.username:
        usernamebefore = (
            f"@{usernamebefore}" if usernamebefore else strings("no_uname")
        )
        usernameafter = (
            f"@{m.from_user.username}"
            if m.from_user.username
            else strings("no_uname")
        )
        msg += strings("uname_change_msg").format(bef=usernamebefore, aft=usernameafter)
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if first_name != m.from_user.first_name:
        msg += strings("firstname_change_msg").format(bef=first_name, aft=m.from_user.first_name)
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if lastname_before != m.from_user.last_name:
        lastname_before = lastname_before or strings("no_last_name")
        lastname_after = m.from_user.last_name or strings("no_last_name")
        msg += strings("lastname_change_msg").format(bef=lastname_before, aft=lastname_after)
        await add_userdata(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
    if msg != "":
        await kirimPesan(m, msg, quote=True)


@app.on_message(filters.group & filters.command("sangmata_set", COMMAND_HANDLER) & ~filters.bot & ~filters.via_bot)
@adminsOnly("can_change_info")
@ratelimiter
@use_chat_lang()
async def set_mataa(_, m, strings):
    if len(m.command) == 1:
        return await kirimPesan(m, strings("set_sangmata_help").format(cmd=m.command[0]))
    if m.command[1] == "on":
        cekset = await is_sangmata_on(m.chat.id)
        if cekset:
            await kirimPesan(m, strings("sangmata_already_on"))
        else:
            await sangmata_on(m.chat.id)
            await kirimPesan(m, strings("sangmata_enabled"))
    elif m.command[1] == "off":
        cekset = await is_sangmata_on(m.chat.id)
        if not cekset:
            await kirimPesan(m, strings("sangmata_already_off"))
        else:
            await sangmata_off(m.chat.id)
            await kirimPesan(m, strings("sangmata_disabled"))
    else:
        await kirimPesan(m, strings("wrong_param"))
