import asyncio
from logging import getLogger

LOGGER = getLogger(__name__)


async def kirimPesan(msg, text: str, reply_markup=None):
    try:
        return await msg.reply(text, disable_web_page_preview=True)
    except FloodWait as e:
        LOGGER.warning(str(e))
        await asyncio.sleep(e.value)
        return await kirimPesan(text)
    except Exception as e:
        LOGGER.error(str(e))
        return
