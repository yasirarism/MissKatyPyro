"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2023-01-11 12:23:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import re
import logging
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram import filters
from misskaty.helper.http import http
from misskaty import app
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.message_utils import *

LOGGER = logging.getLogger(__name__)
LKTERBIT_DICT = {}

def split_arr(arr, size):
     arrs = []
     while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
     arrs.append(arr)
     return arrs

# Terbit21 GetData
async def getDataTerbit21(chat_id, message_id, kueri, CurrentPage):
    if not LKTERBIT_DICT.get(message_id):
        if not kueri:
            terbitjson = (await http.get('https://yasirapi.eu.org/terbit21')).json()
        else:
            terbitjson = (await http.get(f'https://yasirapi.eu.org/terbit21?q={kueri}')).json()
        if not terbitjson.get("result"):
            return await app.send_message(
                chat_id=chat_id,
                reply_to_message_id=message_id,
                text="Sorry, could not find any results!"
            )
        LKTERBIT_DICT[message_id] = [split_arr(terbitjson["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(LKTERBIT_DICT[message_id][0])
        
        TerbitRes = ""
        for c, i in enumerate(LKTERBIT_DICT[message_id][0][index], start=1):
            if kueri:
                TerbitRes = f"<b>#Terbit21 Results For:</b> <code>{kueri}</code>\n\n"
            else:
                TerbitRes = "<b>#Terbit21 Latest:</b>\n🌀 Use /lk21 [title] to start search with title.\n\n"
            TerbitRes += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
            TerbitRes += "\n" if re.search(r"Complete|Ongoing", i["kategori"]) else f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n"
        INGNORE_CHAR = "[]"
        TerbitRes = ''.join(i for i in TerbitRes if not i in INGNORE_CHAR)
        return TerbitRes, PageLen
    except (IndexError, KeyError):
        await app.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text="Sorry, could not find any results!"
        )

# LK21 GetData
async def getDatalk21(chat_id, message_id, kueri, CurrentPage):
    if not LKTERBIT_DICT.get(message_id):
        if not kueri:
            lk21json = (await http.get('https://yasirapi.eu.org/lk21')).json()
        else:
            lk21json = (await http.get(f'https://yasirapi.eu.org/lk21?q={kueri}')).json()
        if not lk21json.get("result"):
            return await app.send_message(
                chat_id=chat_id,
                reply_to_message_id=message_id,
                text="Sorry could not find any matching results!"
            )
        LKTERBIT_DICT[message_id] = [split_arr(lk21json["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(LKTERBIT_DICT[message_id][0])
        
        lkResult = ""
        for c, i in enumerate(LKTERBIT_DICT[message_id][0][index], start=1):
            if kueri:
                lkResult = f"<b>#Layarkaca21 Results For:</b> <code>{kueri}</code>\n\n"
            else:
                lkResult = "<b>#Layarkaca21 Latest:</b>\n🌀 Use /lk21 [title] to start search with title.\n\n"
            lkResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
            lkResult += "\n" if re.search(r"Complete|Ongoing", i["kategori"]) else f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n"
        INGNORE_CHAR = "[]"
        lkResult = ''.join(i for i in lkResult if not i in INGNORE_CHAR)
        return lkResult, PageLen
    except (IndexError, KeyError):
        await app.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text="Sorry could not find any matching results!"
        )

# Terbit21 CMD
@app.on_message(filters.command(['terbit21'], COMMAND_HANDLER))
async def terbit21_s(client, message):
    chat_id = message.chat.id 
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = None
    pesan = await message.reply("Getting data from Terbit21..")
    CurrentPage = 1
    terbitres, PageLen = await getDatalk21(chat_id, pesan.id, kueri, CurrentPage)
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_terbit21#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, terbitres, reply_markup=keyboard)

# LK21 CMD
@app.on_message(filters.command(['lk21'], COMMAND_HANDLER))
async def lk21_s(client, message):
    chat_id = message.chat.id 
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = None
    pesan = await message.reply("Getting data from LK21..")
    CurrentPage = 1
    lkres, PageLen = await getDatalk21(chat_id, pesan.id, kueri, CurrentPage)
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lk21#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, lkres, reply_markup=keyboard)

# Lk21 Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_terbit21#' in query.data))
async def terbit21page_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    chat_id = callback_query.message.chat.id 
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = LKTERBIT_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    terbitres, PageLen = await getDataTerbit21(chat_id, message_id, kueri, CurrentPage)

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_terbit21#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, terbitres, reply_markup=keyboard)

# Lk21 Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_lk21#' in query.data))
async def lk21page_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    chat_id = callback_query.message.chat.id 
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = LKTERBIT_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    lkres, PageLen = await getDatalk21(chat_id, message_id, kueri, CurrentPage)

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lk21#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, lkres, reply_markup=keyboard)