import asyncio
from logging import getLogger

from pyrogram.errors import ChatWriteForbidden, FloodWait, MessageNotModified

LOGGER = getLogger(__name__)

# handler for TG function, so need write exception in every code


async def kirimPesan(msg, text: str, disable_web_page_preview=True, reply_markup=None):
    try:
        return await msg.reply(text=text, disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup)
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await kirimPesan(msg, text=text, disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup)
    except ChatWriteForbidden:
        return await msg.leave()
    except Exception as e:
        LOGGER.error(str(e))


async def editPesan(msg, text: str, disable_web_page_preview=True, reply_markup=None):
    try:
        return await msg.edit(text=text, disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup)
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await editPesan(msg, text=text, disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup)
    except MessageNotModified:
        return
    except Exception as e:
        LOGGER.error(str(e))


async def hapusPesan(msg):
    try:
        return await msg.delete()
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await hapusPesan(msg)
    except Exception as e:
        LOGGER.error(str(e))
