import asyncio
from logging import getLogger

from pyrogram.errors import ChatWriteForbidden, FloodWait, MessageNotModified, ChatAdminRequired, MessageDeleteForbidden, MessageIdInvalid, MessageEmpty

LOGGER = getLogger(__name__)

# handler for TG function, so need write exception in every code


# Send MSG Pyro
async def kirimPesan(msg, text, **kwargs):
    try:
        return await msg.reply(text, **kwargs)
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await kirimPesan(msg, text, **kwargs)
    except (ChatWriteForbidden, ChatAdminRequired):
        LOGGER.info(f"Leaving from {msg.chat.title} [{msg.chat.id}] because doesn't have admin permission.")
        return await msg.leave()
    except Exception as e:
        LOGGER.error(str(e))
        return


# Edit MSG Pyro
async def editPesan(msg, text, **kwargs):
    try:
        return await msg.edit(text, **kwargs)
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await editPesan(msg, text, **kwargs)
    except (MessageNotModified, MessageIdInvalid, MessageEmpty):
        return
    except Exception as e:
        LOGGER.error(str(e))
        return


async def hapusPesan(msg):
    try:
        return await msg.delete()
    except (MessageDeleteForbidden, ChatAdminRequired):
        return
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await hapusPesan(msg)
    except Exception as e:
        LOGGER.error(str(e))
