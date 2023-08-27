import asyncio
import os
from datetime import datetime, timedelta
from logging import getLogger
from typing import Union

import emoji
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message

from database.afk_db import is_cleanmode_on
from database.users_chats_db import db
from misskaty import app, cleanmode

LOGGER = getLogger("MissKaty")
BANNED = {}

loop = asyncio.get_event_loop()


async def put_cleanmode(chat_id, message_id):
    if chat_id not in cleanmode:
        cleanmode[chat_id] = []
    time_now = datetime.now()
    put = {
        "msg_id": message_id,
        "timer_after": time_now + timedelta(minutes=1),
    }
    cleanmode[chat_id].append(put)


async def auto_clean():
    while not await asyncio.sleep(30):
        try:
            for chat_id in cleanmode:
                if not await is_cleanmode_on(chat_id):
                    continue
                for x in cleanmode[chat_id]:
                    if datetime.now() <= x["timer_after"]:
                        continue
                    try:
                        await app.delete_messages(chat_id, x["msg_id"])
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except:
                        continue
        except:
            continue


# temp db for banned
class temp:
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None


def demoji(teks):
    return emoji.emojize(f":{teks.replace(' ', '_').replace('-', '_')}:")


async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Succes"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        LOGGER.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        LOGGER.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        LOGGER.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception:
        return False, "Error"


def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker",
        ):
            if obj := getattr(msg, message_type):
                setattr(obj, "message_type", message_type)
                return obj


def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if len(message.entities) > 1 and message.entities[1].type == "text_mention":
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)
