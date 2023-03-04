import logging, os

import cloudscraper
from bs4 import BeautifulSoup
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import filters

from misskaty import app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.core.message_utils import *
from misskaty.helper import http
from misskaty.vars import COMMAND_HANDLER

from .web_scraper import split_arr

LOGGER = logging.getLogger(__name__)
SUB_TITLE_DICT = {}
SUB_DL_DICT = {}

# Get list title based on query
async def getTitleSub(msg, kueri, CurrentPage, user):
    if not SUB_TITLE_DICT.get(msg.id):
        sdata = []
        scraper = cloudscraper.create_scraper()
        param = {"query": kueri}
        r  = scraper.post("https://subscene.com/subtitles/searchbytitle", data=param).text
        soup = BeautifulSoup(r,"lxml")
        lists = soup.find("div", {"class": "search-result"})
        entry = lists.find_all("div", {"class":"title"})
        # if "Tidak Ditemukan" in entry[0].text:
        #     await editPesan(msg, f"Sorry, could not find any result for: {kueri}")
        #     return None, 0, None
        for sub in entry:
            title = sub.find('a').text
            link = f"https://subscene.com{sub.find('a').get('href')}"
            sdata.append({"title": title, "link": link})
        SUB_TITLE_DICT[msg.id] = [split_arr(sdata, 10), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SUB_TITLE_DICT[msg.id][0])
        extractbtn1 = []
        extractbtn2 = []
        subResult = f"<b>#Subscene Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(SUB_TITLE_DICT[msg.id][0][index], start=1):
            subResult += f"<b>{c}. <a href='{i['link']}'>{i['title']}</a></b>\n"
            if c < 6:
                extractbtn1.append(InlineButton(c, f"sublist#{CurrentPage}#{c}#{msg.id}#{user}"))
            else:
                extractbtn2.append(InlineButton(c, f"sublist#{CurrentPage}#{c}#{msg.id}#{user}"))
        subResult = "".join(i for i in subResult if i not in "[]")
        return subResult, PageLen, extractbtn1, extractbtn2
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None

# Get list all subtitles from title
async def getListSub(msg, link, CurrentPage, user):
    if not SUB_DL_DICT.get(msg.id):
        sdata = []
        scraper = cloudscraper.create_scraper()
        r = scraper.get(link).text
        soup = BeautifulSoup(r,"lxml")
        for i in soup.findAll(class_="a1"):
            lang = i.find("a").findAll("span")[0].text.strip()
            title = i.find("a").findAll("span")[1].text.strip()
            if i.find(class_="l r neutral-icon"):
                rate = "😐"
            elif i.find(class_="l r positive-icon"):
                rate = "🥰"
            else:
                rate = "☹️"
            dllink = f"https://subscene.com{i.find('a').get('href')}"
            sdata.append({"title": title, "lang": lang, "rate": rate, "link": dllink})
        SUB_DL_DICT[msg.id] = [split_arr(sdata, 10), link]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SUB_DL_DICT[msg.id][0])
        extractbtn1 = []
        extractbtn2 = []
        subResult = f"<b>#Subscene Results For:</b> <code>{link}</code>\n\n"
        for c, i in enumerate(SUB_DL_DICT[msg.id][0][index], start=1):
            subResult += f"<b>{c}. {i['title']}</b> [{i['rate']}]\n{i['lang']}\n"
            if c < 6:
                extractbtn1.append(InlineButton(c, f"extractsubs#{CurrentPage}#{c}#{msg.id}#{user}"))
            else:
                extractbtn2.append(InlineButton(c, f"extractsubs#{CurrentPage}#{c}#{msg.id}#{user}"))
        subResult = "".join(i for i in subResult if i not in "[]")
        return subResult, PageLen, extractbtn1, extractbtn2
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None

# Subscene CMD
@app.on_message(filters.command(["subscene"], COMMAND_HANDLER))
@ratelimiter
async def subsceneCMD(client, message):
    kueri = " ".join(message.command[1:])
    if not kueri:
        return await kirimPesan(message, f"ℹ️ Please add query after CMD!\nEx: <code>/{message.command[0]} Jurassic World</code>")
    pesan = await kirimPesan(message, "⏳ Please wait, getting data from subscene..", quote=True)
    CurrentPage = 1
    subres, PageLen, btn1, btn2 = await getTitleSub(pesan, kueri, CurrentPage, message.from_user.id)
    if not subres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, "subscenepage#{number}" + f"#{pesan.id}#{message.from_user.id}")
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(InlineButton("❌ Close", f"close#{message.from_user.id}"))
    await editPesan(pesan, subres, disable_web_page_preview=True, reply_markup=keyboard)

# Callback list title
@app.on_callback_query(filters.create(lambda _, __, query: "subscenepage#" in query.data))
@ratelimiter
async def subpage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split("#")[2])
    CurrentPage = int(callback_query.data.split("#")[1])
    try:
        kueri = SUB_TITLE_DICT[message_id][1]
    except KeyError:
        await callback_query.answer("Invalid callback data, please send CMD again..")
        await asyncio.sleep(3)
        return await callback_query.message.delete()

    try:
        subres, PageLen, btn1, btn2 = await getTitleSub(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, "subscenepage#{number}" + f"#{message_id}#{callback_query.from_user.id}")
    keyboard.row(InlineButton("👇 Get Subtitle List", "Hmmm"))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(InlineButton("❌ Close", f"close#{callback_query.from_user.id}"))
    await editPesan(callback_query.message, subres, disable_web_page_preview=True, reply_markup=keyboard)

# Callback list title
@app.on_callback_query(filters.create(lambda _, __, query: "sublist#" in query.data))
@ratelimiter
async def subdlpage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split("#")[4]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split("#")[3])
    CurrentPage = int(callback_query.data.split("#")[1])
    try:
        link = SUB_TITLE_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except KeyError:
        await callback_query.answer("Invalid callback data, please send CMD again..")
        await asyncio.sleep(3)
        return await callback_query.message.delete()

    try:
        subres, PageLen, btn1, btn2 = await getListSub(callback_query.message, link, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, "sublist#{number}" + f"#{idlink}#{message_id}#{callback_query.from_user.id}")
    keyboard.row(InlineButton("👇 Download Subtitle", "Hmmm"))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(InlineButton("❌ Close", f"close#{callback_query.from_user.id}"))
    await editPesan(callback_query.message, subres, disable_web_page_preview=True, reply_markup=keyboard)

# Callback dl subtitle
@app.on_callback_query(filters.create(lambda _, __, query: "extractsubs#" in query.data))
@ratelimiter
async def dlsub_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split("#")[4]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split("#")[3])
    CurrentPage = int(callback_query.data.split("#")[1])
    try:
        link = SUB_DL_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except KeyError:
        await callback_query.answer("Invalid callback data, please send CMD again..")
        await asyncio.sleep(3)
        return await callback_query.message.delete()
    scraper = cloudscraper.create_scraper()
    req = scraper.get("https://subscene.com/subtitles/the-big-bang-theory-first-season/english/136037").text
    soup = BeautifulSoup(req,"lxml")
    judul = soup.find("div", {"class": "bread"}).find("a").get("href").split("/")[4]
    downloadlink = soup.find("div", {"class": "download"}).find('a')
    download = 'https://subscene.com'+downloadlink['href']
    dl = scraper.get(download)
    open(f"{judul}.zip", "wb").write(dl.content)
    await callback_query.message.reply_document(f"{judul}.zip")
    os.remove(f"{judul}.zip")
