# Code copy from https://github.com/AbirHasan2005/Forward-Client
from bot import user
from os import environ
from pyrogram import filters
from asyncio import sleep
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from info import FORWARD_FILTERS, BLOCK_FILES_WITHOUT_EXTENSIONS, BLOCKED_EXTENSIONS, FORWARD_TO_CHAT_ID, FORWARD_FROM_CHAT_ID, MINIMUM_FILE_SIZE


async def FilterMessage(message: Message):
    if (message.forward_from
            or message.forward_from_chat) and ("forwarded"
                                               not in FORWARD_FILTERS):
        return 400
    if (len(FORWARD_FILTERS)
            == 9) or ((message.video and ("video" in FORWARD_FILTERS)) or
                      (message.document and ("document" in FORWARD_FILTERS)) or
                      (message.photo and ("photo" in FORWARD_FILTERS)) or
                      (message.audio and ("audio" in FORWARD_FILTERS)) or
                      (message.text and ("text" in FORWARD_FILTERS)) or
                      (message.animation and ("gif" in FORWARD_FILTERS)) or
                      (message.poll and ("poll" in FORWARD_FILTERS)) or
                      (message.sticker and ("sticker" in FORWARD_FILTERS))):
        return 200
    else:
        return 400


async def CheckBlockedExt(event: Message):
    media = event.document or event.video or event.audio or event.animation
    if (BLOCK_FILES_WITHOUT_EXTENSIONS is True) and ("."
                                                     not in media.file_name):
        return True
    if (media is not None) and (media.file_name is not None):
        _file = media.file_name.rsplit(".", 1)
        if len(_file) == 2:
            if (_file[-1].lower()
                    in BLOCKED_EXTENSIONS) or (_file[-1].upper()
                                               in BLOCKED_EXTENSIONS):
                return True
            else:
                return False
        else:
            return False


async def CheckFileSize(msg: Message):
    media = msg.video or msg.document or msg.audio or msg.photo or msg.animation
    if (MINIMUM_FILE_SIZE
            is not None) and (media.file_size < int(MINIMUM_FILE_SIZE)):
        return False
    else:
        return True


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
        for i in range(len(FORWARD_TO_CHAT_ID)):
            try:
                await msg.copy(FORWARD_TO_CHAT_ID[i])
            except FloodWait as e:
                await sleep(e.value)
                await client.send_message(
                    chat_id="me",
                    text=f"#FloodWait: Stopped Forwarder for `{e.x}s`!")
                await sleep(10)
                await ForwardMessage(client, msg)
            except Exception as err:
                await client.send_message(
                    chat_id="me",
                    text=
                    f"#ERROR: `{err}`\n\nUnable to Forward Message to `{str(FORWARD_TO_CHAT_ID[i])}`"
                )
    except Exception as err:
        await client.send_message(chat_id="me", text=f"#ERROR: `{err}`")


@user.on_message(filters.text | filters.media)
async def forwarder(client: user, message: Message):
    if message.chat.id in FORWARD_FROM_CHAT_ID:
        try_forward = await ForwardMessage(client, message)
        if try_forward == 400:
            return