import re
import time
from bot import app
from pyrogram import filters, enums
from database.afk_db import remove_afk, is_afk
from bot.utils.human_read import get_readable_time2

# Detect user that AFK
chat_watcher_group = 1


@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=chat_watcher_group,
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.first_name
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.BOT_COMMAND:
                if entity.offset == 0 and entity.length == 4:
                    text = message.text or message.caption
                    command_ = (text[0:4]).lower()
                    if command_ == "/afk":
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
                msg += f"**{user_name[:25]}** kembali online dan telah AFK selama {seenago}\n\n"
            if afktype == "text_reason":
                msg += f"**{user_name[:25]}** kembali online dan telah AFK selama {seenago}\n\nAlasan: `{reasonafk}`\n\n"
            if afktype == "animation":
                if str(reasonafk) == "None":
                    await message.reply_animation(
                        data,
                        caption=
                        f"**{user_name[:25]}** kembali online dan telah AFK selama {seenago}\n\n",
                    )
                else:
                    await message.reply_animation(
                        data,
                        caption=
                        f"**{user_name[:25]}** kembali online dan telah AFK selama {seenago}\n\Alasan: `{reasonafk}`\n\n",
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=
                        f"**{user_name[:25]}** kembali online dan telah AFK selama {seenago}\n\n",
                    )
                else:
                    await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=
                        f"**{user_name[:25]}** kembali online dan telah AFK selama {seenago}\n\Alasan: `{reasonafk}`\n\n",
                    )
        except:
            msg += f"**{user_name[:25]}** kembali online.\n\n"

    # Replied to a User which is AFK
    if message.reply_to_message:
        try:
            replied_first_name = (
                message.reply_to_message.from_user.first_name)
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
                        msg += f"**{replied_first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\n"
                    if afktype == "text_reason":
                        msg += f"**{replied_first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\nAlasan: `{reasonafk}`\n\n"
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            await message.reply_animation(
                                data,
                                caption=
                                f"**{replied_first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\n",
                            )
                        else:
                            await message.reply_animation(
                                data,
                                caption=
                                f"**{replied_first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\Alasan: `{reasonafk}`\n\n",
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=
                                f"**{replied_first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\n",
                            )
                        else:
                            await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=
                                f"**{replied_first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\nAlasan: `{reasonafk}`\n\n",
                            )
                except Exception as e:
                    msg += f"**{replied_first_name}** sedang AFK\n\n"
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
                        seenago = get_readable_time2(
                            (int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += f"**{user.first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\n"
                        if afktype == "text_reason":
                            msg += f"**{user.first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\nAlasan: `{reasonafk}`\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(
                                    data,
                                    caption=
                                    f"**{user.first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\n",
                                )
                            else:
                                await message.reply_animation(
                                    data,
                                    caption=
                                    f"**{user.first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\nAlasan: `{reasonafk}`\n\n",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=
                                    f"**{user.first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\n",
                                )
                            else:
                                await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=
                                    f"**{user.first_name[:25]}** sedang AFK sejak {seenago} yang lalu.\n\nAlasan: `{reasonafk}`\n\n",
                                )
                    except:
                        msg += (f"**{user.first_name[:25]}** sedang AFK\n\n")
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
                        seenago = get_readable_time2(
                            (int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += f"**{first_name[:25]}** sedang AFK sejak {seenago} yang lalu\n\n"
                        if afktype == "text_reason":
                            msg += f"**{first_name[:25]}** sedang AFK sejak {seenago} yang lalu\n\nAlasan: `{reasonafk}`\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                await message.reply_animation(
                                    data,
                                    caption=
                                    f"**{first_name[:25]}** sedang AFK sejak {seenago} yang lalu\n\n",
                                )
                            else:
                                await message.reply_animation(
                                    data,
                                    caption=
                                    f"**{first_name[:25]}** sedang AFK sejak {seenago} yang lalu\n\nAlasan: `{reasonafk}`\n\n",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=
                                    f"**{first_name[:25]}** sedang AFK sejak {seenago} yang lalu\n\n",
                                )
                            else:
                                await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=
                                    f"**{first_name[:25]}** sedang AFK sejak {seenago} yang lalu\n\nAlasan: `{reasonafk}`\n\n",
                                )
                    except:
                        msg += f"**{first_name[:25]}** is AFK\n\n"
            j += 1
    if msg != "":
        try:
            return await message.reply_text(msg, disable_web_page_preview=True)
        except:
            return
