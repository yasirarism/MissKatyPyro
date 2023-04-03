#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiAFKBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiAFKBot/blob/master/LICENSE >
#
# All rights reserved.
#

# Modified plugin by me from https://github.com/TeamYukki/YukkiAFKBot to make compatible with pyrogram v2
import time
import re

from pyrogram import filters, enums

from database.afk_db import add_afk, cleanmode_off, cleanmode_on, is_afk, remove_afk
from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.permissions import adminsOnly
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.message_utils import kirimPesan
from misskaty.helper import get_readable_time2
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER
from utils import put_cleanmode

__MODULE__ = "AFK"
__HELP__ = """/afk [Reason > Optional] - Tell others that you are AFK (Away From Keyboard), so that your boyfriend or girlfriend won't look for you 💔.
/afk [reply to media] - AFK with media.
/afkdel - Enable auto delete AFK message in group (Only for group admin). Default is **Enable**.
Just type something in group to remove AFK Status."""


# Handle set AFK Command
@capture_err
@app.on_message(filters.command(["afk"], COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def active_afk(_, message, strings):
    if message.sender_chat:
        return await kirimPesan(message, strings("no_channel"))
    user_id = message.from_user.id
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await remove_afk(user_id)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time2((int(time.time() - timeafk)))
            if afktype == "animation":
                send = (
                    await message.reply_animation(
                        data,
                        caption=strings("on_afk_msg_no_r").format(usr=message.from_user.mention, id=message.from_user.id, tm=seenago),
                    )
                    if str(reasonafk) == "None"
                    else await message.reply_animation(
                        data,
                        caption=strings("on_afk_msg_with_r").format(usr=message.from_user.mention, id=message.from_user.id, tm=seenago, reas=reasonafk),
                    )
                )
            elif afktype == "photo":
                send = (
                    await message.reply_photo(
                        photo=f"downloads/{user_id}.jpg",
                        caption=strings("on_afk_msg_no_r").format(usr=message.from_user.mention, id=message.from_user.id, tm=seenago),
                    )
                    if str(reasonafk) == "None"
                    else await message.reply_photo(
                        photo=f"downloads/{user_id}.jpg",
                        caption=strings("on_afk_msg_with_r").format(usr=message.from_user.first_name, tm=seenago, reas=reasonafk),
                    )
                )
            elif afktype == "text":
                send = await message.reply_text(
                    caption=strings("on_afk_msg_no_r").format(usr=message.from_user.mention, id=message.from_user.id, tm=seenago),
                    disable_web_page_preview=True,
                )
            elif afktype == "text_reason":
                send = await message.reply_text(
                    caption=strings("on_afk_msg_with_r").format(usr=message.from_user.mention, id=message.from_user.id, tm=seenago, reas=reasonafk),
                    disable_web_page_preview=True,
                )
        except Exception:
            send = await message.reply_text(
                strings("is_online").format(usr=message.from_user.first_name),
                disable_web_page_preview=True,
            )
        await put_cleanmode(message.chat.id, send.id)
        return
    if len(message.command) == 1 and not message.reply_to_message:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(message.command) > 1 and not message.reply_to_message:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "text_reason",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif len(message.command) == 1 and message.reply_to_message.animation:
        _data = message.reply_to_message.animation.file_id
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": None,
        }
    elif len(message.command) > 1 and message.reply_to_message.animation:
        _data = message.reply_to_message.animation.file_id
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": _reason,
        }
    elif len(message.command) == 1 and message.reply_to_message.photo:
        await app.download_media(message.reply_to_message, file_name=f"{user_id}.jpg")
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(message.command) > 1 and message.reply_to_message.photo:
        await app.download_media(message.reply_to_message, file_name=f"{user_id}.jpg")
        _reason = message.text.split(None, 1)[1].strip()
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif len(message.command) == 1 and message.reply_to_message.sticker:
        if message.reply_to_message.sticker.is_animated:
            details = {
                "type": "text",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
        else:
            await app.download_media(message.reply_to_message, file_name=f"{user_id}.jpg")
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
    elif len(message.command) > 1 and message.reply_to_message.sticker:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        if message.reply_to_message.sticker.is_animated:
            details = {
                "type": "text_reason",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
        else:
            await app.download_media(message.reply_to_message, file_name=f"{user_id}.jpg")
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
    else:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }

    await add_afk(user_id, details)
    send = await kirimPesan(message, strings("now_afk").format(usr=message.from_user.mention, id=message.from_user.id))
    await put_cleanmode(message.chat.id, send.id)


@app.on_message(filters.command("afkdel", COMMAND_HANDLER) & filters.group)
@ratelimiter
@adminsOnly("can_change_info")
@use_chat_lang()
async def afk_state(_, message, strings):
    if not message.from_user:
        return
    if len(message.command) == 1:
        return await kirimPesan(message, strings("afkdel_help").format(cmd=message.command[0]))
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await cleanmode_on(chat_id)
        await kirimPesan(message, strings("afkdel_enable"))
    elif state == "disable":
        await cleanmode_off(chat_id)
        await kirimPesan(message, strings("afkdel_disable"))
    else:
        await kirimPesan(message, strings("afkdel_help").format(cmd=message.command[0]))


# Detect user that AFK based on Yukki Repo
@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=1,
)
@use_chat_lang()
async def chat_watcher_func(client, message, strings):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.mention
    if message.entities:
        possible = ["/afk", f"/afk@{client.me.username}", "!afk"]
        message_text = message.text or message.caption
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.BOT_COMMAND:
                if (message_text[0 : 0 + entity.length]).lower() in possible:
                    return

    msg = ""
    replied_user_id = 0

    # Self AFK
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time2((int(time.time() - timeafk)))
            if afktype == "text":
                msg += strings("on_afk_msg_no_r").format(usr=user_name, id=userid, tm=seenago)
            if afktype == "text_reason":
                msg += strings("on_afk_msg_with_r").format(usr=user_name, id=userid, tm=seenago, reas=reasonafk)
            if afktype == "animation":
                if str(reasonafk) == "None":
                    send = await message.reply_animation(
                        data,
                        caption=strings("on_afk_msg_no_r").format(usr=user_name, id=userid, tm=seenago),
                    )
                else:
                    send = await message.reply_animation(
                        data,
                        caption=strings("on_afk_msg_with_r").format(usr=user_name, id=userid, tm=seenago, reas=reasonafk),
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    send = await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=strings("on_afk_msg_no_r").format(usr=user_name, id=userid, tm=seenago),
                    )
                else:
                    send = await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=strings("on_afk_msg_with_r").format(usr=user_name, id=userid, tm=seenago, reas=reasonafk),
                    )
        except:
            msg += strings("is_online").format(usr=user_name, id=userid)

    # Replied to a User which is AFK
    if message.reply_to_message:
        try:
            replied_first_name = message.reply_to_message.from_user.mention
            replied_user_id = message.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                try:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    data = reasondb["data"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time2((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += strings("is_afk_msg_no_r").format(usr=replied_first_name, id=replied_user_id, tm=seenago)
                    if afktype == "text_reason":
                        msg += strings("is_afk_msg_with_r").format(usr=replied_first_name, id=replied_user_id, tm=seenago, reas=reasonafk)
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            send = await message.reply_animation(
                                data,
                                caption=strings("is_afk_msg_no_r").format(usr=replied_first_name, id=replied_user_id, tm=seenago),
                            )
                        else:
                            send = await message.reply_animation(
                                data,
                                caption=strings("is_afk_msg_with_r").format(usr=replied_first_name, id=replied_user_id, tm=seenago, reas=reasonafk),
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            send = await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=strings("is_afk_msg_no_r").format(usr=replied_first_name, id=replied_user_id, tm=seenago),
                            )
                        else:
                            send = await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=strings("is_afk_msg_with_r").format(usr=replied_first_name, id=replied_user_id, tm=seenago, reas=reasonafk),
                            )
                except Exception:
                    msg += strings("is_afk").format(usr=replied_first_name, id=replied_user_id)
        except:
            pass

    # If username or mentioned user is AFK
    if message.entities:
        entity = message.entities
        j = 0
        for x in range(len(entity)):
            if (entity[j].type) == enums.MessageEntityType.MENTION:
                found = re.findall("@([_0-9a-zA-Z]+)", message.text)
                try:
                    get_user = found[j]
                    user = await app.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time2((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += strings("is_afk_msg_no_r").format(usr=user.first_name[:25], id=user.id, tm=seenago)
                        if afktype == "text_reason":
                            msg += strings("is_afk_msg_with_r").format(usr=user.first_name[:25], id=user.id, tm=seenago, reas=reasonafk)
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await message.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_no_r").format(usr=user.first_name[:25], id=user.id, tm=seenago),
                                )
                            else:
                                send = await message.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_with_r").format(usr=user.first_name[:25], id=user.id, tm=seenago, reas=reasonafk),
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=strings("is_afk_msg_no_r").format(usr=user.first_name[:25], id=user.id, tm=seenago),
                                )
                            else:
                                send = await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=strings("is_afk_msg_with_r").format(usr=user.first_name[:25], id=user.id, tm=seenago, reas=reasonafk),
                                )
                    except:
                        msg += strings("is_afk").format(usr=user.first_name[:25], id=user.id)
            elif (entity[j].type) == enums.MessageEntityType.TEXT_MENTION:
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time2((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += strings("is_afk_msg_no_r").format(usr=first_name[:25], id=user_id, tm=seenago)
                        if afktype == "text_reason":
                            msg += strings("is_afk_msg_with_r").format(usr=first_name[:25], id=user_id, tm=seenago, reas=reasonafk)
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await message.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_no_r").format(usr=first_name[:25], id=user_id, tm=seenago),
                                )
                            else:
                                send = await message.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_with_r").format(usr=first_name[:25], id=user_id, tm=seenago, reas=reasonafk),
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=strings("is_afk_msg_no_r").format(usr=first_name[:25], id=user_id, tm=seenago),
                                )
                            else:
                                send = await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=strings("is_afk_msg_with_r").format(usr=first_name[:25], id=user_id, tm=seenago, reas=reasonafk),
                                )
                    except:
                        msg += strings("is_afk").format(usr=first_name[:25], id=user_id)
            j += 1
    if msg != "":
        try:
            send = await message.reply_text(msg, disable_web_page_preview=True)
        except:
            pass
    try:
        await put_cleanmode(message.chat.id, send.id)
    except:
        pass
