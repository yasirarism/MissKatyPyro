import asyncio

from pykeyboard import InlineKeyboard
from pyrogram import filters
from misskaty.helper.http import http
from misskaty.helper.tools import get_random_string
from misskaty import app
from misskaty.vars import COMMAND_HANDLER

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
    message_id = message.id 
    chat_id = message.chat.id 
    kueri = ' '.join(message.command[1:])
    if not kueri:
        message = await app.ask(
            message.chat.id,
            'Now give any word for query!'
        )
        kueri = message.text
    
    CurrentPage = 1
    lkres, PageLen = await getDatalk21(chat_id, message_id, kueri, CurrentPage)
    
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'pagination_lk21#{number}' + f'#{message.from_user.id}')
    await message.reply(
        text=f"{lkres}",
        reply_markup=keyboard
    ) 

@app.on_callback_query(filters.create(lambda _, __, query: 'pagination_lk21#' in query.data))
async def lk21page_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[2]):
        return await callback_query.answer("Not yours..", True)
    message_id = callback_query.message.id
    chat_id = callback_query.message.chat.id 
    CurrentPage = int(callback_query.data.split('#')[1]) 
    kueri = LK_DICT[message_id][1]

    try:
        lkres, PageLen = await getDatalk21(chat_id, message_id, kueri, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'pagination_lk21#{number}' + f'#{callback_query.from_user.id}')
    await app.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=lkres,
        reply_markup=keyboard
    )