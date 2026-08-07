"""Misc chat utilities shared by plugins: user extraction, file-id
retrieval, broadcast helper and the in-memory ``temp`` state container."""

import asyncio
import logging
import os
from typing import Union

import emoji
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message

from database.users_chats_db import db

LOGGER = logging.getLogger("MissKaty")


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
    while True:
        try:
            await message.copy(chat_id=user_id)
            return True, "Success"
        except FloodWait as e:
            await asyncio.sleep(e.value)
            continue
        except InputUserDeactivated:
            await db.delete_user(int(user_id))
            LOGGER.info(f"{user_id} - Removed from Database, since deleted account.")
            return False, "Deleted"
        except UserIsBlocked:
            LOGGER.info(f"{user_id} - Blocked the bot.")
            return False, "Blocked"
        except PeerIdInvalid:
            await db.delete_user(int(user_id))
            LOGGER.info(f"{user_id} - PeerIdInvalid")
            return False, "Error"
        except Exception:
            return False, "Error"


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


def extract_user_and_name(message: Message) -> Union[int, str]:
    """extracts (user_id, user_first_name) from a message (sync helper)"""
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            message.entities
            and len(message.entities) > 1
            and message.entities[1].type.value == "text_mention"
        ):
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
