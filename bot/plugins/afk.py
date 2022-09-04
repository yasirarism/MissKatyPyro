# Sample menggunakan modul motor mongodb
import time, asyncio
from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER
from database.afk_db import remove_afk, is_afk, add_afk
from bot.utils.human_read import get_readable_time2
from bot.utils.decorator import capture_err


__MODULE__ = "AFK"
__HELP__ = """/afk - Tandai dirimu sedang AFK
I tell users that you are away if you are, so they dont need to be hanging for your reply. Just type
"""

# Handle set AFK Command
@capture_err
@app.on_message(filters.command(["afk"], COMMAND_HANDLER))
async def active_afk(_, message):
    if message.sender_chat:
        return
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
            if afktype == "text":
                return await message.reply_text(
                    f"**{message.from_user.first_name}** telah kembali online dan sudah AFK selama {seenago}",
                    disable_web_page_preview=True,
                )
            if afktype == "text_reason":
                return await message.reply_text(
                    f"**{message.from_user.first_name}** telah kembali online dan sudah AFK selama {seenago}\n\nReason: `{reasonafk}`",
                    disable_web_page_preview=True,
                )
            if afktype == "animation":
                if str(reasonafk) == "None":
                    return await message.reply_animation(
                        data,
                        caption=
                        f"**{message.from_user.first_name}** is back online and was away for {seenago}",
                    )
                else:
                    return await message.reply_animation(
                        data,
                        caption=
                        f"**{message.from_user.first_name}** is back online and was away for {seenago}\n\nReason: `{reasonafk}",
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    return await message.reply_photo(
                        photo=f"downloads/{user_id}.jpg",
                        caption=
                        f"**{message.from_user.first_name}** is back online and was away for {seenago}",
                    )
                else:
                    return await message.reply_photo(
                        photo=f"downloads/{user_id}.jpg",
                        caption=
                        f"**{message.from_user.first_name}** is back online and was away for {seenago}\n\nALasan: `{reasonafk}`",
                    )
        except Exception:
            return await message.reply_text(
                f"**{message.from_user.first_name}** kembali online.",
                disable_web_page_preview=True,
            )
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
        await app.download_media(message.reply_to_message,
                                 file_name=f"{user_id}.jpg")
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(message.command) > 1 and message.reply_to_message.photo:
        await app.download_media(message.reply_to_message,
                                 file_name=f"{user_id}.jpg")
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
            await app.download_media(message.reply_to_message,
                                     file_name=f"{user_id}.jpg")
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
            await app.download_media(message.reply_to_message,
                                     file_name=f"{user_id}.jpg")
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
    pesan = await message.reply_text(
        f"{message.from_user.mention} [<code>{message.from_user.id}</code>] sekarang AFK! Pesan ini akan terhapus dalam waktu 10 detik."
    )
    await asyncio.sleep(10)
    await pesan.delete()