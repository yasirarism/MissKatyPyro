import asyncio
import logging
from pykeyboard import InlineKeyboard
from pyrogram import filters
from misskaty.helper.http import http
from misskaty.helper.tools import get_random_string
from misskaty import app
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.message_utils import *

LOGGER = logging.getLogger(__name__)
LK_DICT = {}

def split_arr(arr, size):
     arrs = []
     while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
     arrs.append(arr)
     return arrs

async def getDatalk21(chat_id, message_id, kueri, CurrentPage):
    if not LK_DICT.get(message_id):
        lk21json = (await http.get(f'https://yasirapi.eu.org/lk21?q={kueri}')).json()
        if not lk21json.get("result"):
            return await app.send_message(
                chat_id=chat_id,
                reply_to_message_id=message_id,
                text=(
                    f"Kueri: {kueri}\n"
                    "Results: Sorry could not find any matching results!"
                )
            )
        LK_DICT[message_id] = [split_arr(lk21json["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(LK_DICT[message_id][0])
        
        msgs = ""
        for c, i in enumerate(LK_DICT[message_id][0][index], start=1):
            msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
        
        lkResult = (
            f"**Hasil pencarian dg kata kunci {kueri}**\n"
            f"{msgs}\n\n"
        )
        
        IGNORE_CHAR = "[]"
        lkResult = ''.join(i for i in lkResult if not i in IGNORE_CHAR)
        
        return (
        lkResult,
        PageLen
        )

    except (
        IndexError
        or KeyError
    ):
        await app.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=(
                f"Kueri: {kueri}\n"
                "Results: Sorry could not find any matching results!"
            )
        )

@app.on_message(filters.command(['lktes'], COMMAND_HANDLER))
async def lk21tes(client, message):
    chat_id = message.chat.id 
    kueri = ' '.join(message.command[1:])
    if not kueri:
        message = await app.ask(
            message.chat.id,
            'Now give any word for query!'
        )
        kueri = message.text
    pesan = await message.reply("Getting data from LK21..")
    CurrentPage = 1
    lkres, PageLen = await getDatalk21(chat_id, pesan.id, kueri, CurrentPage)
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lk21#{number}' + f'#{pesan.id}#{message.from_user.id}')
    await editPesan(pesan, lkres, reply_markup=keyboard)

@app.on_callback_query(filters.create(lambda _, __, query: 'page_lk21#' in query.data))
async def lk21page_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    chat_id = callback_query.message.chat.id 
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = LK_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        lkres, PageLen = await getDatalk21(chat_id, message_id, kueri, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lk21#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    await editPesan(callback_query.message, lkres, reply_markup=keyboard)