"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2023-01-23 19:41:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import filters
from pyrogram.errors import QueryIdInvalid
from pyrogram.types import CallbackQuery, Message

from misskaty import app
from misskaty.helper import Cache, fetch
from misskaty.plugins.web_scraper import split_arr
from misskaty.vars import COMMAND_HANDLER

PYPI_DICT = Cache(filename="pypi_cache.db", path="cache", in_memory=False)


async def getDataPypi(msg, kueri, CurrentPage, user):
    if not PYPI_DICT.get(msg.id):
        pypijson = (await fetch.get(f"https://yasirapi.eu.org/pypi?q={kueri}")).json()
        if not pypijson.get("result"):
            await msg.edit_msg("Sorry could not find any matching results!", del_in=6)
            return None, 0, None
        PYPI_DICT.add(msg.id, [split_arr(pypijson["result"], 6), kueri], timeout=1600)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(PYPI_DICT[msg.id][0])
        extractbtn = []
        pypiResult = f"<b>#Pypi Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(PYPI_DICT[msg.id][0][index], start=1):
            pypiResult += f"<b>{c}.</b> <a href='{i['url']}'>{i['name']} {i['version']}</a>\n<b>Created:</b> <code>{i['created']}</code>\n<b>Desc:</b> <code>{i['description']}</code>\n\n"
            extractbtn.append(
                InlineButton(c, f"pypidata#{CurrentPage}#{c}#{user}#{msg.id}")
            )
        pypiResult = "".join(i for i in pypiResult if i not in "[]")
        return pypiResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await msg.edit_msg("Sorry could not find any matching results!", del_in=6)
        return None, 0, None


@app.on_message(filters.command(["pypi"], COMMAND_HANDLER))
async def pypi_s(_, ctx: Message):
    kueri = " ".join(ctx.command[1:])
    if not kueri:
        return await ctx.reply_msg(
            "Please add query after command. Ex: <code>/pypi pyrogram</code>", del_in=6
        )
    pesan = await ctx.reply_msg("⏳ Please wait, getting data from pypi..", quote=True)
    CurrentPage = 1
    pypires, PageLen, btn = await getDataPypi(
        pesan, kueri, CurrentPage, ctx.from_user.id
    )
    if not pypires:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen, CurrentPage, "page_pypi#{number}" + f"#{pesan.id}#{ctx.from_user.id}"
    )
    keyboard.row(InlineButton("👇 Get Info ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(InlineButton("❌ Close", f"close#{ctx.from_user.id}"))
    await pesan.edit_msg(pypires, reply_markup=keyboard)


@app.on_callback_query(filters.create(lambda _, __, query: "page_pypi#" in query.data))
async def pypipage_callback(_, callback_query: CallbackQuery):
    if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split("#")[2])
    CurrentPage = int(callback_query.data.split("#")[1])
    try:
        kueri = PYPI_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer(
            "Invalid callback data, please send CMD again.."
        )
    except QueryIdInvalid:
        return

    try:
        pypires, PageLen, btn = await getDataPypi(
            callback_query.message, kueri, CurrentPage, callback_query.from_user.id
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_pypi#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(InlineButton("❌ Close", f"close#{callback_query.from_user.id}"))
    await callback_query.message.edit_msg(pypires, reply_markup=keyboard)


@app.on_callback_query(filters.create(lambda _, __, query: "pypidata#" in query.data))
async def pypi_getdata(_, callback_query: CallbackQuery):
    if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split("#")[4])
    CurrentPage = int(callback_query.data.split("#")[1])
    try:
        pkgname = PYPI_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("name")
    except KeyError:
        return await callback_query.answer(
            "Invalid callback data, please send CMD again.."
        )

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            "↩️ Back",
            f"page_pypi#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}"),
    )
    try:
        html = await fetch.get(f"https://pypi.org/pypi/{pkgname}/json")
        res = html.json()
        requirement = (
            "".join(f"{i}, " for i in res["info"].get("requires_dist"))
            if res["info"].get("requires_dist")
            else "Unknown"
        )
        msg = ""
        msg += f"<b>Package Name:</b> {res['info'].get('name', 'Unknown')}\n"
        msg += f"<b>Version:</b> {res['info'].get('version', 'Unknown')}\n"
        msg += f"<b>License:</b> {res['info'].get('license', 'Unknown')}\n"
        msg += f"<b>Author:</b> {res['info'].get('author', 'Unknown')}\n"
        msg += f"<b>Author Email:</b> {res['info'].get('author_email', 'Unknown')}\n"
        msg += f"<b>Requirements:</b> {requirement}\n"
        msg += (
            f"<b>Requires Python:</b> {res['info'].get('requires_python', 'Unknown')}\n"
        )
        msg += f"<b>HomePage:</b> {res['info'].get('home_page', 'Unknown')}\n"
        msg += f"<b>Bug Track:</b> {res['info'].get('vulnerabilities', 'Unknown')}\n"
        if res["info"].get("project_urls"):
            msg += f"<b>Docs Url:</b> {res['info']['project_urls'].get('Documentation', 'Unknown')}\n"
        msg += f"<b>Description:</b> {res['info'].get('summary', 'Unknown')}\n"
        msg += (
            f"<b>Pip Command:</b> pip3 install {res['info'].get('name', 'Unknown')}\n"
        )
        msg += f"<b>Keywords:</b> {res['info'].get('keywords', 'Unknown')}\n"
        await callback_query.message.edit_msg(msg, reply_markup=keyboard)
    except Exception as err:
        await callback_query.message.edit_msg(f"ERROR: {err}", reply_markup=keyboard)
