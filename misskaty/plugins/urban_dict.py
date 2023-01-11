import asyncio

from pykeyboard import InlineKeyboard
from pyrogram import filters
from misskaty.helper.http import http
from misskaty import app
from misskaty.vars import COMMAND_HANDLER


async def getData(chat_id, message_id, GetWord, CurrentPage):
    UDJson = (await http.get(
            f'https://api.urbandictionary.com/v0/define?term={GetWord}')).json()

    if not 'list' in UDJson:
        CNMessage = await app.send_message(
            chat_id==chat_id,
            reply_to_message_id=message_id,
            text=(
                f"Word: {GetWord}\n"
                "Results: Sorry could not find any matching results!"
            )
        )
        await asyncio.sleep(5)
        await CNMessage.delete()
        return
    try:
        index = int(CurrentPage - 1)
        PageLen = len(UDJson['list'])
        
        UDReasult = (
            f"**Definition of {GetWord}**\n"
            f"{UDJson['list'][index]['definition']}\n\n"
            "**📌 Examples**\n"
            f"__{UDJson['list'][index]['example']}__"
        )
        
        INGNORE_CHAR = "[]"
        UDFReasult = ''.join(i for i in UDReasult if not i in INGNORE_CHAR)
        
        return (
        UDFReasult,
        PageLen
        )

    except (
        IndexError
        or KeyError
    ):
        CNMessage = await app.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=(
                f"Word: {GetWord}\n"
                "Results: Sorry could not find any matching results!"
            )
        )
        await asyncio.sleep(5)
        await CNMessage.delete()

@app.on_message(filters.command(['ud'], COMMAND_HANDLER))
async def urbanDictionary(client, message):
    message_id = message.id 
    chat_id = message.chat.id 
    GetWord = ' '.join(message.command[1:])
    if not GetWord:
        message = await app.ask(
            message.chat.id,
            'Now give any word for query!'
        )
        GetWord = message.text
    
    CurrentPage = 1
    UDReasult, PageLen = await getData(chat_id, message_id, GetWord, CurrentPage)
    
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'pagination_keyboard#{number}' + f'#{GetWord}')
    await message.reply(
        text=f"{UDReasult}",
        reply_markup=keyboard
    ) 

@app.on_callback_query(filters.create(lambda _, __, query: 'pagination_keyboard#' in query.data))
async def ud_callback(client, callback_query):
    
    message_id = callback_query.message.id
    chat_id = callback_query.message.chat.id 
    CurrentPage = int(callback_query.data.split('#')[1]) 
    GetWord = callback_query.data.split('#')[2]

    try:
        UDReasult, PageLen = await getData(chat_id, message_id, GetWord, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'pagination_keyboard#{number}' + f'#{GetWord}')
    await app.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=UDReasult,
        reply_markup=keyboard
    )