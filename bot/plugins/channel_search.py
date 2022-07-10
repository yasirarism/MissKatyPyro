from pyrogram import filters, enums, emoji
from bot import app
from database.ia_filterdb import save_file, get_search_results
import logging
from pyrogram.errors import QueryIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultCachedDocument
from utils import get_size

media_filter = filters.document | filters.video | filters.audio


@app.on_message(filters.chat(-1001210537567) & media_filter)
async def mediasave(_, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return
    logging.info(media)
    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)


@app.on_inline_query()
async def answer_file(_, query):

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=string)
    files, next_offset, total = await get_search_results(string,
                                                         file_type=file_type,
                                                         max_results=10,
                                                         offset=offset)

    for file in files:
        title = file.file_name
        size = get_size(file.file_size)
        f_caption = file.caption
        if f_caption is None:
            f_caption = f"{file.file_name}"
        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                document_file_id=file.file_id,
                caption=f_caption,
                description=
                f'Size: {get_size(file.file_size)}\nType: {file.file_type}',
                reply_markup=reply_markup))

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
        if string:
            switch_pm_text += f" for {string}"
        try:
            await query.answer(results=results,
                               is_personal=True,
                               cache_time=30,
                               switch_pm_text=switch_pm_text,
                               switch_pm_parameter="start",
                               next_offset=str(next_offset))
        except QueryIdInvalid:
            pass
        except Exception as e:
            logging.exception(str(e))
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} No results'
        if string:
            switch_pm_text += f' for "{string}"'

        await query.answer(results=[],
                           is_personal=True,
                           cache_time=30,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")


def get_reply_markup(query):
    buttons = [[
        InlineKeyboardButton('Search again',
                             switch_inline_query_current_chat=query)
    ]]
    return InlineKeyboardMarkup(buttons)
