# Code copy from https://github.com/AbirHasan2005/Forward-Client
from asyncio import sleep
from logging import getLogger

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from misskaty import user
from misskaty.vars import (
    BLOCK_FILES_WITHOUT_EXTENSIONS,
    BLOCKED_EXTENSIONS,
    FORWARD_FILTERS,
    FORWARD_FROM_CHAT_ID,
    FORWARD_TO_CHAT_ID,
    MINIMUM_FILE_SIZE,
)

LOGGER = getLogger("MissKaty")


async def FilterMessage(message: Message):
    if (message.forward_from or message.forward_from_chat) and (
        "forwarded" not in FORWARD_FILTERS
    ):
        return 400
    if (len(FORWARD_FILTERS) == 9) or (
        (message.video and ("video" in FORWARD_FILTERS))
        or (message.document and ("document" in FORWARD_FILTERS))
        or (message.photo and ("photo" in FORWARD_FILTERS))
        or (message.audio and ("audio" in FORWARD_FILTERS))
        or (message.text and ("text" in FORWARD_FILTERS))
        or (message.animation and ("gif" in FORWARD_FILTERS))
        or (message.poll and ("poll" in FORWARD_FILTERS))
        or (message.sticker and ("sticker" in FORWARD_FILTERS))
    ):
        return 200
    else:
        return 400


async def CheckBlockedExt(event: Message):
    media = event.document or event.video or event.audio or event.animation
    if (BLOCK_FILES_WITHOUT_EXTENSIONS is True) and ("." not in media.file_name):
        return True
    if (media is not None) and (media.file_name is not None):
        _file = media.file_name.rsplit(".", 1)
        if len(_file) == 2:
            return (
                _file[-1].lower() in BLOCKED_EXTENSIONS
                or _file[-1].upper() in BLOCKED_EXTENSIONS
            )

        else:
            return False


async def CheckFileSize(msg: Message):
    media = msg.video or msg.document or msg.audio or msg.photo or msg.animation
    return MINIMUM_FILE_SIZE is None or media.file_size >= int(MINIMUM_FILE_SIZE)


async def ForwardMessage(client: user, msg: Message):
    try:
        ## --- Check 1 --- ##
        can_forward = await FilterMessage(message=msg)
        if can_forward == 400:
            return 400
        ## --- Check 2 --- ##
        has_blocked_ext = await CheckBlockedExt(event=msg)
        if has_blocked_ext is True:
            return 400
        ## --- Check 3 --- ##
        file_size_passed = await CheckFileSize(msg=msg)
        if file_size_passed is False:
            return 400
        ## --- Check 4 --- ##
        for item in FORWARD_TO_CHAT_ID:
            try:
                await msg.copy(item)
            except FloodWait as e:
                await sleep(e.value)
                LOGGER.warning(f"#FloodWait: Stopped Forwarder for {e.x}s!")
                await ForwardMessage(client, msg)
            except Exception as err:
                LOGGER.warning(
                    f"#ERROR: {err}\n\nUnable to Forward Message to {str(item)}, reason: <code>{err}</code>"
                )
    except:
        pass


@user.on_message((filters.text | filters.media) & filters.chat(FORWARD_FROM_CHAT_ID))
async def forwardubot(client: user, message: Message):
    try_forward = await ForwardMessage(client, message)
    if try_forward == 400:
        return
