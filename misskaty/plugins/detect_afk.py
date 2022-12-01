import re
import time
import asyncio
from misskaty import app
from pyrogram import filters, enums
from database.afk_db import remove_afk, is_afk
from misskaty.helper.human_read import get_readable_time2

# Detect user that AFK based on Yukki Repo
@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=1,
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.first_name
    if message.entities:
        possible = ["/afk", f"/afk@MissKatyRoBot", "!afk"]
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
                msg += f"**{user_name[:25]}** is back online and was away for {seenago}\n\n"
            if afktype == "text_reason":
                msg += f"**{user_name[:25]}** is back online and was away for {seenago}\n\n**Reason:** {reasonafk}\n\n"
            if afktype == "animation":
                if str(reasonafk) == "None":
                    await message.reply_animation(
                        data,
                        caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\n",
                    )
                else:
                    await message.reply_animation(
                        data,
                        caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\n**Reason:** {reasonafk}\n\n",
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\n",
                    )
                else:
                    await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=f"**{user_name[:25]}** is back online and was away for {seenago}\n\n**Reason:** {reasonafk}\n\n",
                    )
        except:
            msg += f"**{user_name[:25]}** is back online.\n\n"

    # Replied to a User which is AFK
    if message.reply_to_message:
        try:
            replied_first_name = message.reply_to_message.from_user.first_name
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
                        msg += f"**{replied_first_name[:25]}** is AFK since {seenago} ago.\n\n"
                    if afktype == "text_reason":
                        msg += f"**{replied_first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n"
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            await message.reply_animation(
                                data,
                                caption=f"**{replied_first_name[:25]}** is AFK since {seenago} ago.\n\n",
                            )
                        else:
                            await message.reply_animation(
                                data,
                                caption=f"**{replied_first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n",
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"**{replied_first_name[:25]}** is AFK since {seenago} ago.\n\n",
                            )
                        else:
                            await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"**{replied_first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n",
                            )
                except Exception:
                    msg += f"**{replied_first_name}** is AFK\n\n"
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
                            msg += f"**{user.first_name[:25]}** is AFK since {seenago} ago.\n\n"
                        if afktype == "text_reason":
                            msg += f"**{user.first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(
                                    data,
                                    caption=f"**{user.first_name[:25]}** is AFK since {seenago} ago.\n\n",
                                )
                            else:
                                await message.reply_animation(
                                    data,
                                    caption=f"**{user.first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason**: {reasonafk}\n\n",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"**{user.first_name[:25]}** is AFK since {seenago} ago.\n\n",
                                )
                            else:
                                await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"**{user.first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n",
                                )
                    except:
                        msg += f"**{user.first_name[:25]}** is AFK\n\n"
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
                            msg += (
                                f"**{first_name[:25]}** is AFK since {seenago} ago.\n\n"
                            )
                        if afktype == "text_reason":
                            msg += f"**{first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(
                                    data,
                                    caption=f"**{first_name[:25]}** is AFK since {seenago} ago.\n\n",
                                )
                            else:
                                await message.reply_animation(
                                    data,
                                    caption=f"**{first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"**{first_name[:25]}** is AFK since {seenago} ago.\n\n",
                                )
                            else:
                                await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"**{first_name[:25]}** is AFK since {seenago} ago.\n\n**Reason:** {reasonafk}\n\n",
                                )
                    except:
                        msg += f"**{first_name[:25]}** is AFK\n\n"
            j += 1
    if msg != "":
        try:
            pesan = await message.reply_text(msg, disable_web_page_preview=True)
            await asyncio.sleep(20)
            await pesan.delete()
        except:
            return
