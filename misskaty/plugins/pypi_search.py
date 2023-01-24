"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2023-01-23 19:41:27
 * @lastModified  2023-01-23 19:41:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import filters

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.helper.http import http
from misskaty.plugins.web_scraper import split_arr, headers
from misskaty.vars import COMMAND_HANDLER

PYPI_DICT = {}

async def getDataPypi(msg, kueri, CurrentPage, user):
    if not PYPI_DICT.get(msg.id):
        pypijson = (await http.get(f'https://yasirapi.eu.org/pypi?q={kueri}')).json()
        if not pypijson.get("result"):
            await editPesan(msg, "Sorry could not find any matching results!")
            return None, 0, None
        PYPI_DICT[msg.id] = [split_arr(pypijson["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(PYPI_DICT[msg.id][0])
        extractbtn = []
        pypiResult = f"<b>#Pypi Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(PYPI_DICT[msg.id][0][index], start=1):
            pypiResult += f"<b>{c}. <a href='{i['url']} {i['version']}'>{i['name']}</a></b>\n<b>Created:</b> <code>{i['created']}</code>\n<b>Desc:</b> <code>{i['description']}</code>\n\n"
            extractbtn.append(
                InlineButton(c, f"pypidata#{CurrentPage}#{c}#{user}#{msg.id}")
            )
        IGNORE_CHAR = "[]"
        pypiResult = ''.join(i for i in pypiResult if not i in IGNORE_CHAR)
        return pypiResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None
    
@app.on_message(filters.command(['pypi'], COMMAND_HANDLER))
async def pypi_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        return await kirimPesan(message, "Please add query after command. Ex: <code>/pypi pyrogram</code>")
    pesan = await kirimPesan(message, "⏳ Please wait, getting data from pypi..", quote=True)
    CurrentPage = 1
    pypires, PageLen, btn = await getDataPypi(pesan, kueri, CurrentPage, message.from_user.id)
    if not pypires: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_pypi#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(InlineButton("👇 Get Info ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, pypires, reply_markup=keyboard)

@app.on_callback_query(filters.create(lambda _, __, query: 'page_pypi#' in query.data))
async def pypipage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = PYPI_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        pypires, PageLen, btn = await getDataPypi(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_pypi#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, pypires, reply_markup=keyboard)

@app.on_callback_query(filters.create(lambda _, __, query: 'pypidata#' in query.data))
async def pypi_getdata(_, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split('#')[4])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        pkgname = PYPI_DICT[message_id][0][CurrentPage-1][idlink-1].get("name")
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton("↩️ Back", f"page_pypi#{CurrentPage}#{message_id}#{callback_query.from_user.id}"),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    try:
        html = await http.get(f"https://pypi.org/pypi/{pkgname}/json", headers=headers)
        res = html.json()
        msg = res["info"]["keywords"]
    except Exception as err:
        await editPesan(callback_query.message, f"ERROR: {err}", reply_markup=keyboard)
        return
    await editPesan(callback_query.message, res, reply_markup=keyboard)
