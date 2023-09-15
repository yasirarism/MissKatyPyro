from pykeyboard import InlineKeyboard
from pyrogram.types import CallbackQuery, Message

from misskaty import app
from misskaty.helper.http import fetch


async def getData(chat_id, message_id, GetWord, CurrentPage):
    UDJson = (
        await fetch.get(f"https://api.urbandictionary.com/v0/define?term={GetWord}")
    ).json()

    if "list" not in UDJson:
        return await app.send_msg(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=f"Word: {GetWord}\nResults: Sorry could not find any matching results!",
            del_in=5,
        )
    try:
        index = int(CurrentPage - 1)
        PageLen = len(UDJson["list"])
        UDReasult = (
            f"**Definition of {GetWord}**\n"
            f"{UDJson['list'][index]['definition']}\n\n"
            "**📌 Examples**\n"
            f"__{UDJson['list'][index]['example']}__"
        )
        UDFReasult = "".join(i for i in UDReasult if i not in "[]")
        return (UDFReasult, PageLen)

    except (IndexError, KeyError):
        await app.send_msg(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=f"Word: {GetWord}\nResults: Sorry could not find any matching results!",
            del_in=5,
        )


@app.on_cmd("ud", no_channel=True)
async def urbanDictionary(_, ctx: Message):
    message_id = ctx.id
    chat_id = ctx.chat.id
    GetWord = " ".join(ctx.command[1:])
    if not GetWord:
        message = await ctx.chat.ask("Now give any word for query!")
        GetWord = message.text

    CurrentPage = 1
    try:
        UDReasult, PageLen = await getData(chat_id, message_id, GetWord, CurrentPage)
    except:
        return await ctx.reply_msg("😭 Failed getting info from urban dictionary.")

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, "pagination_urban#{number}" + f"#{GetWord}")
    await ctx.reply_msg(text=f"{UDReasult}", reply_markup=keyboard)


@app.on_cb("pagination_urban#")
async def ud_callback(_, callback_query: CallbackQuery):
    message_id = callback_query.message.id
    chat_id = callback_query.message.chat.id
    CurrentPage = int(callback_query.data.split("#")[1])
    GetWord = callback_query.data.split("#")[2]

    try:
        UDReasult, PageLen = await getData(chat_id, message_id, GetWord, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, "pagination_urban#{number}" + f"#{GetWord}")
    await callback_query.message.edit_msg(text=UDReasult, reply_markup=keyboard)
