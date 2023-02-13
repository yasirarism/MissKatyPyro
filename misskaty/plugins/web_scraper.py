"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2023-01-11 12:23:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import re
import logging
from bs4 import BeautifulSoup
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from misskaty.helper.http import http
from misskaty.helper.kuso_utils import Kusonime
from misskaty import app
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.message_utils import *

__MODULE__ = "WebScraper"
__HELP__ = """
/melongmovie [query <optional>] - Scrape website data from MelongMovie Web.
/lk21 [query <optional>] - Scrape website data from LayarKaca21.
/pahe [query <optional>] - Scrape website data from Pahe.li.
/terbit21 [query <optional>] - Scrape website data from Terbit21.
/savefilm21 [query <optional>] - Scrape website data from Savefilm21.
/movieku [query <optional>] - Scrape website data from Movieku.cc
/kusonime [query <optional>] - Scrape website data from Kusonime
/lendrive [query <optional>] - Scrape website data from Lendrive
/gomov [query <optional>] - Scrape website data from GoMov.
"""

headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}

LOGGER = logging.getLogger(__name__)
SCRAP_DICT = {}
data_kuso = {}

def split_arr(arr, size: 5):
     arrs = []
     while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
     arrs.append(arr)
     return arrs

# Terbit21 GetData
async def getDataTerbit21(msg, kueri, CurrentPage):
    if not SCRAP_DICT.get(msg.id):
        if not kueri:
            terbitjson = (await http.get('https://yasirapi.eu.org/terbit21')).json()
        else:
            terbitjson = (await http.get(f'https://yasirapi.eu.org/terbit21?q={kueri}')).json()
        if not terbitjson.get("result"):
            await editPesan(msg, "Sorry, could not find any results!")
            return None, None
        SCRAP_DICT[msg.id] = [split_arr(terbitjson["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        
        if kueri:
            TerbitRes = f"<b>#Terbit21 Results For:</b> <code>{kueri}</code>\n\n"
        else:
            TerbitRes = "<b>#Terbit21 Latest:</b>\n🌀 Use /terbit21 [title] to start search with title.\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            TerbitRes += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
            TerbitRes += "\n" if re.search(r"Complete|Ongoing", i["kategori"]) else f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n"
        IGNORE_CHAR = "[]"
        TerbitRes = ''.join(i for i in TerbitRes if not i in IGNORE_CHAR)
        return TerbitRes, PageLen
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry, could not find any results!")
        return None, None

# LK21 GetData
async def getDatalk21(msg, kueri, CurrentPage):
    if not SCRAP_DICT.get(msg.id):
        if not kueri:
            lk21json = (await http.get('https://yasirapi.eu.org/lk21')).json()
        else:
            lk21json = (await http.get(f'https://yasirapi.eu.org/lk21?q={kueri}')).json()
        if not lk21json.get("result"):
            await editPesan(msg, "Sorry could not find any matching results!")
            return None, None
        SCRAP_DICT[msg.id] = [split_arr(lk21json["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        
        if kueri:
            lkResult = f"<b>#Layarkaca21 Results For:</b> <code>{kueri}</code>\n\n"
        else:
            lkResult = "<b>#Layarkaca21 Latest:</b>\n🌀 Use /lk21 [title] to start search with title.\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            lkResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
            lkResult += "\n" if re.search(r"Complete|Ongoing", i["kategori"]) else f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n"
        IGNORE_CHAR = "[]"
        lkResult = ''.join(i for i in lkResult if not i in IGNORE_CHAR)
        return lkResult, PageLen
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, None

# Pahe GetData
async def getDataPahe(msg, kueri, CurrentPage):
    if not SCRAP_DICT.get(msg.id):
        pahejson = (await http.get(f'https://yasirapi.eu.org/pahe?q={kueri}')).json()
        if not pahejson.get("result"):
            await editPesan(msg, "Sorry could not find any matching results!")
            return None, None
        SCRAP_DICT[msg.id] = [split_arr(pahejson["result"], 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        
        paheResult = f"<b>#Pahe Results For:</b> <code>{kueri}</code>\n\n" if kueri else f"<b>#Pahe Latest:</b>\n🌀 Use /pahe [title] to start search with title.\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            paheResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n\n"
        IGNORE_CHAR = "[]"
        paheResult = ''.join(i for i in paheResult if not i in IGNORE_CHAR)
        return paheResult, PageLen
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, None

# Kusonime GetData
async def getDataKuso(msg, kueri, CurrentPage, user):
    if not SCRAP_DICT.get(msg.id):
        kusodata = []
        data = await http.get(f'https://kusonime.com/?s={kueri}', headers=headers)
        res = BeautifulSoup(data.text, "lxml").find_all("h2", {"class": "episodeye"})
        for i in res:
            ress = i.find_all("a")[0]
            title = ress.text
            link = ress["href"]
            kusodata.append({"title": title, "link": link})
        if not kusodata:
            await editPesan(msg, "Sorry could not find any results!")
            return None, 0, None, None
        SCRAP_DICT[msg.id] = [split_arr(kusodata, 10), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn1 = []
        extractbtn2 = []

        kusoResult = f"<b>#Kusonime Latest Post\n\n" if kueri == "" else f"<b>#Kusonime Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            kusoResult += f"<b>{c}</b>. {i['title']}\n{i['link']}\n\n"
            if c < 6:
                extractbtn1.append(
                    InlineButton(c, f"kusoextract#{CurrentPage}#{c}#{user}#{msg.id}")
                )
            else:
                extractbtn2.append(
                    InlineButton(c, f"kusoextract#{CurrentPage}#{c}#{user}#{msg.id}")
                )
        IGNORE_CHAR = "[]"
        kusoResult = ''.join(i for i in kusoResult if not i in IGNORE_CHAR)
        return kusoResult, PageLen, extractbtn1, extractbtn2
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None, None

# Movieku GetData
async def getDataMovieku(msg, kueri, CurrentPage):
    if not SCRAP_DICT.get(msg.id):
        moviekudata = []
        data = await http.get(f'https://107.152.37.223/?s={kueri}', headers=headers)
        r = BeautifulSoup(data.text, "lxml")
        res = r.find_all(class_="bx")
        for i in res:
            judul = i.find_all("a")[0]["title"]
            link = i.find_all("a")[0]["href"]
            typ = i.find(class_="overlay").text
            typee = typ.strip() if typ.strip() != "" else "~" 
            moviekudata.append({"judul": judul, "link": link, "type": typee})
        if not moviekudata:
            await editPesan(msg, "Sorry could not find any results!")
            return None, None
        SCRAP_DICT[msg.id] = [split_arr(moviekudata, 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        
        moviekuResult = f"<b>#Movieku Latest:</b>\n🌀 Use /movieku [title] to start search with title.\n\n" if kueri == "" else f"<b>#Movieku Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            moviekuResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Quality/Status:</b> {i['type']}\n<b>Extract:</b> <code>/movieku_scrap {i['link']}</code>\n\n"
        IGNORE_CHAR = "[]"
        moviekuResult = ''.join(i for i in moviekuResult if not i in IGNORE_CHAR)
        return moviekuResult, PageLen
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, None

# Savefilm21 GetData
async def getDataSavefilm21(msg, kueri, CurrentPage, user):
    if not SCRAP_DICT.get(msg.id):
        sfdata = []
        data = await http.get(f'https://185.99.135.215/?s={kueri}', headers=headers)
        text = BeautifulSoup(data.text, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Tidak Ditemukan" in entry[0].text:
            if not kueri:
                await editPesan(msg, "Sorry, could not find any result")
                return None, 0, None
            else:
                await editPesan(msg, f"Sorry, could not find any result for: {kueri}")
                return None, 0, None
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            sfdata.append({"judul": judul, "link": link, "genre": genre})
        SCRAP_DICT[msg.id] = [split_arr(sfdata, 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []
        sfResult = f"<b>#SaveFilm21 Latest:</b>\n🌀 Use /savefilm21 [title] to start search with title.\n\n" if kueri == "" else f"<b>#Savefilm21 Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            sfResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> {i['genre']}\n\n"
            extractbtn.append(
                InlineButton(c, f"sf21extract#{CurrentPage}#{c}#{user}#{msg.id}")
            )
        IGNORE_CHAR = "[]"
        sfResult = ''.join(i for i in sfResult if not i in IGNORE_CHAR)
        return sfResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None

# Lendrive GetData
async def getDataLendrive(msg, kueri, CurrentPage, user):
    if not SCRAP_DICT.get(msg.id):
        data = await http.get(f'https://lendrive.web.id/?s={kueri}', headers=headers)
        soup = BeautifulSoup(data.text, "lxml")
        lenddata = []
        for o in soup.find_all(class_="bsx"):
            title = o.find("a")["title"]
            link = o.find("a")["href"]
            status = o.find(class_="epx").text
            kualitas = o.find(class_="typez TV").text if o.find(class_="typez TV") else o.find(class_="typez BD")
            lenddata.append({"judul": title, "link": link, "quality": kualitas, "status": status})
        if not lenddata:
            await editPesan(msg, "Sorry could not find any results!")
            return None, 0, None
        SCRAP_DICT[msg.id] = [split_arr(lenddata, 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []
        
        lenddataResult = f"<b>#LenDrive Latest:</b>\n🌀 Use /lendrive [title] to start search with title.\n\n" if kueri == "" else f"<b>#LenDrive Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            lenddataResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Quality:</b> {i['quality']}\n<b>Status:</b> {i['status']}\n\n"
            extractbtn.append(
                InlineButton(c, f"lendriveextract#{CurrentPage}#{c}#{user}#{msg.id}")
            )
        IGNORE_CHAR = "[]"
        lenddataResult = ''.join(i for i in lenddataResult if not i in IGNORE_CHAR)
        return lenddataResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None

# MelongMovie GetData
async def getDataMelong(msg, kueri, CurrentPage, user):
    if not SCRAP_DICT.get(msg.id):
        data = await http.get(f'http://167.99.31.48/?s={kueri}', headers=headers)
        bs4 = BeautifulSoup(data.text, "lxml")
        melongdata = []
        for res in bs4.select(".box"):
            dd = res.select("a")
            url = dd[0]["href"]
            title = dd[0]["title"]
            try:
                quality = dd[0].find(class_="quality").text
            except:
                quality = "N/A"
            melongdata.append({"judul": title, "link": url, "quality": quality})
        if not melongdata:
            await editPesan(msg, "Sorry could not find any results!")
            return None, 0, None
        SCRAP_DICT[msg.id] = [split_arr(melongdata, 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []

        melongResult = f"<b>#MelongMovie Latest:</b>\n🌀 Use /melongmovie [title] to start search with title.\n\n" if kueri == "" else f"<b>#MelongMovie Results For:</b> <code>{kueri}</code>\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            melongResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Quality:</b> {i['quality']}\n\n"
            extractbtn.append(
                InlineButton(c, f"melongextract#{CurrentPage}#{c}#{user}#{msg.id}")
            )
        IGNORE_CHAR = "[]"
        melongResult = ''.join(i for i in melongResult if not i in IGNORE_CHAR)
        return melongResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None

# GoMov GetData
async def getDataGomov(msg, kueri, CurrentPage, user):
    if not SCRAP_DICT.get(msg.id):
        gomovv = await http.get(f'https://185.173.38.216/?s={kueri}', headers=headers)
        text = BeautifulSoup(gomovv.text, "lxml")
        entry = text.find_all(class_="entry-header")
        if entry[0].text.strip() == "Nothing Found":
            if not kueri:
                await editPesan(msg, "Sorry, i could not find anything.")
                return None, 0, None
            else:
                await editPesan(msg, f"Sorry, i could not find query: {kueri}")
                return None, 0, None
        data = []
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            data.append({"judul": judul, "link": link, "genre": genre})
        SCRAP_DICT[msg.id] = [split_arr(data, 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []
        
        gomovResult = f"<b>#Gomov Results For:</b> <code>{kueri}</code>\n\n" if kueri else f"<b>#Gomov Latest:</b>\n🌀 Use /gomov [title] to start search with title.\n\n"
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            gomovResult += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n\n"
            if not re.search(r"Series", i["genre"]):
                extractbtn.append(
                    InlineButton(c, f"gomovextract#{CurrentPage}#{c}#{user}#{msg.id}")
                )
        gomovResult += "Some result will not appear in extract button because unsupported link."
        IGNORE_CHAR = "[]"
        gomovResult = ''.join(i for i in gomovResult if not i in IGNORE_CHAR)
        return gomovResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await editPesan(msg, "Sorry could not find any matching results!")
        return None, 0, None

# Terbit21 CMD
@app.on_message(filters.command(['terbit21'], COMMAND_HANDLER))
async def terbit21_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = None
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Terbit21..", quote=True)
    CurrentPage = 1
    terbitres, PageLen = await getDataTerbit21(pesan, kueri, CurrentPage)
    if not terbitres: return
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
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from LK21..", quote=True)
    CurrentPage = 1
    lkres, PageLen = await getDatalk21(pesan, kueri, CurrentPage)
    if not lkres: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lk21#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, lkres, disable_web_page_preview=True, reply_markup=keyboard)

# Pahe CMD
@app.on_message(filters.command(['pahe'], COMMAND_HANDLER))
async def pahe_s(client, message):
    chat_id = message.chat.id 
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Pahe Web..", quote=True)
    CurrentPage = 1
    paheres, PageLen = await getDataPahe(pesan, kueri, CurrentPage)
    if not paheres: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_pahe#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, paheres, reply_markup=keyboard)

# Gomov CMD
@app.on_message(filters.command(['gomov'], COMMAND_HANDLER))
async def gomov_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data Gomov Web..", quote=True)
    CurrentPage = 1
    gomovres, PageLen, btn = await getDataGomov(pesan, kueri, CurrentPage, message.from_user.id)
    if not gomovres: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_gomov#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, gomovres, reply_markup=keyboard)

# MelongMovie CMD
@app.on_message(filters.command(['melongmovie'], COMMAND_HANDLER))
async def melong_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Melongmovie..", quote=True)
    CurrentPage = 1
    melongres, PageLen, btn = await getDataMelong(pesan, kueri, CurrentPage, message.from_user.id)
    if not melongres: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_melong#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, melongres, reply_markup=keyboard)

# Savefilm21 CMD
@app.on_message(filters.command(['savefilm21'], COMMAND_HANDLER))
async def savefilm_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Savefilm21..", quote=True)
    CurrentPage = 1
    savefilmres, PageLen, btn = await getDataSavefilm21(pesan, kueri, CurrentPage, message.from_user.id)
    if not savefilmres: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_savefilm#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, savefilmres, reply_markup=keyboard)

# Kusonime CMD
@app.on_message(filters.command(['kusonime'], COMMAND_HANDLER))
async def kusonime_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Kusonime..", quote=True)
    CurrentPage = 1
    kusores, PageLen, btn1, btn2 = await getDataKuso(pesan, kueri, CurrentPage, message.from_user.id)
    if not kusores: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_kuso#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, kusores, reply_markup=keyboard)

# Lendrive CMD
@app.on_message(filters.command(['lendrive'], COMMAND_HANDLER))
async def lendrive_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Lendrive..", quote=True)
    CurrentPage = 1
    lendres, PageLen, btn = await getDataLendrive(pesan, kueri, CurrentPage, message.from_user.id)
    if not lendres: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lendrive#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, lendres, reply_markup=keyboard)

# Movieku CMD
@app.on_message(filters.command(['movieku'], COMMAND_HANDLER))
async def movieku_s(client, message):
    kueri = ' '.join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await kirimPesan(message, "⏳ Please wait, scraping data from Movieku..", quote=True)
    CurrentPage = 1
    moviekures, PageLen = await getDataMovieku(pesan, kueri, CurrentPage)
    if not moviekures: return
    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_movieku#{number}' + f'#{pesan.id}#{message.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{message.from_user.id}")
    )
    await editPesan(pesan, moviekures, reply_markup=keyboard)

# Savefillm21 Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_savefilm#' in query.data))
async def savefilmpage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        savefilmres, PageLen, btn = await getDataSavefilm21(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_savefilm#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, savefilmres, reply_markup=keyboard)

# Kuso Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_kuso#' in query.data))
async def kusopage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        kusores, PageLen, btn1, btn2 = await getDataKuso(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_kuso#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, kusores, reply_markup=keyboard)

# Lendrive Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_lendrive#' in query.data))
async def moviekupage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        lendres, PageLen, btn = await getDataLendrive(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lendrive#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, lendres, reply_markup=keyboard)

# Movieku Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_movieku#' in query.data))
async def moviekupage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        moviekures, PageLen = await getDataMovieku(callback_query.message, kueri, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_movieku#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, moviekures, reply_markup=keyboard)

# Terbit21 Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_terbit21#' in query.data))
async def terbit21page_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        terbitres, PageLen = await getDataTerbit21(callback_query.message, kueri, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_terbit21#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, terbitres, reply_markup=keyboard)

# Page Callback Melong
@app.on_callback_query(filters.create(lambda _, __, query: 'page_melong#' in query.data))
async def melongpage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        terbitres, PageLen, btn = await getDataMelong(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_melong#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
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
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        lkres, PageLen = await getDatalk21(callback_query.message, kueri, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_lk21#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, lkres, reply_markup=keyboard)

# Pahe Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_pahe#' in query.data))
async def pahepage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        lkres, PageLen = await getDataPahe(callback_query.message, kueri, CurrentPage)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_pahe#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, lkres, reply_markup=keyboard)

# Gomov Page Callback
@app.on_callback_query(filters.create(lambda _, __, query: 'page_gomov#' in query.data))
async def gomovpage_callback(client, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    message_id = int(callback_query.data.split('#')[2])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        kueri = SCRAP_DICT[message_id][1]
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    try:
        gomovres, PageLen, btn = await getDataGomov(callback_query.message, kueri, CurrentPage, callback_query.from_user.id)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(PageLen, CurrentPage, 'page_gomov#{number}' + f'#{message_id}#{callback_query.from_user.id}')
    keyboard.row(InlineButton("👇 Extract Data ", "Hmmm"))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    await editPesan(callback_query.message, gomovres, reply_markup=keyboard)

### Scrape DDL Link From Web ###
# Kusonime DDL
@app.on_callback_query(filters.create(lambda _, __, query: 'kusoextract#' in query.data))
async def kusonime_scrap(_, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split('#')[4])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        link = SCRAP_DICT[message_id][0][CurrentPage-1][idlink-1].get("link")
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    kuso = Kusonime()
    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton("↩️ Back", f"page_kuso#{CurrentPage}#{message_id}#{callback_query.from_user.id}"),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    try:
        init_url = data_kuso.get(link, None)
        if init_url:
            ph = init_url.get("ph_url")
            await editPesan(callback_query.message, f"<b>Scrape result from {link}</b>:\n\n{ph}", reply_markup=keyboard, disable_web_page_preview=False)
            return
        tgh = await kuso.telegraph(link, message_id)
        if tgh["error"]:
            await editPesan(callback_query.message, f"ERROR: {tgh['error_message']}", reply_markup=keyboard)
            return
    except Exception as err:
        await editPesan(callback_query.message, f"ERROR: {err}", reply_markup=keyboard)
        return
    data_kuso[link] = {"ph_url": tgh["url"]}
    await editPesan(callback_query.message, f"<b>Scrape result from</b> <code>{link}</code>:\n\n{tgh['url']}", reply_markup=keyboard, disable_web_page_preview=False)

# Savefilm21 DDL
@app.on_callback_query(filters.create(lambda _, __, query: 'sf21extract#' in query.data))
async def savefilm21_scrap(_, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split('#')[4])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        link = SCRAP_DICT[message_id][0][CurrentPage-1][idlink-1].get("link")
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton("↩️ Back", f"page_savefilm#{CurrentPage}#{message_id}#{callback_query.from_user.id}"),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    try:
        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="button button-shadow")
        res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
    except Exception as err:
        await editPesan(callback_query.message, f"ERROR: {err}", reply_markup=keyboard)
        return
    await editPesan(callback_query.message, f"<b>Scrape result from</b> <code>{link}</code>:\n\n{res}", reply_markup=keyboard)


# Scrape Link Download Movieku.CC
@app.on_message(filters.command(["movieku_scrap"], COMMAND_HANDLER))
async def muviku_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="smokeurl")
        data = []
        for i in res:
            for b in range(len(i.find_all("a"))):
                link = i.find_all("a")[b]["href"]
                kualitas = i.find_all("a")[b].text
                # print(f"{kualitas}\n{link
                data.append({"link": link, "kualitas": kualitas})
        if not data:
            return await message.reply("Oops, data film tidak ditemukan.")
        res = "".join(f"<b>Host: {i['kualitas']}</b>\n{i['link']}\n\n" for i in data)
        await message.reply(res)
    except IndexError:
        return await message.reply(f"Gunakan command /{message.command[0]} <b>[link]</b> untuk scrap link download")
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")

# Scrape DDL Link Melongmovie
@app.on_callback_query(filters.create(lambda _, __, query: 'melongextract#' in query.data))
async def melong_scrap(_, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split('#')[4])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        link = SCRAP_DICT[message_id][0][CurrentPage-1][idlink-1].get("link")
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton("↩️ Back", f"page_melong#{CurrentPage}#{message_id}#{callback_query.from_user.id}"),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    try:
        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        rep = ""
        for ep in soup.findAll(text=re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
            hardsub = ep.findPrevious("div")
            softsub = ep.findNext("div")
            rep += f"{hardsub}\n{softsub}"
    except Exception as err:
        await editPesan(callback_query.message, f"ERROR: {err}", reply_markup=keyboard)
        return
    await editPesan(callback_query.message, f"<b>Scrape result from</b> <code>{link}</code>:\n\n{rep}", reply_markup=keyboard)

# Scrape DDL Link Gomov
@app.on_callback_query(filters.create(lambda _, __, query: 'gomovextract#' in query.data))
async def gomov_dl(_, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split('#')[4])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        link = SCRAP_DICT[message_id][0][CurrentPage-1][idlink-1].get("link")
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton("↩️ Back", f"page_gomov#{CurrentPage}#{message_id}#{callback_query.from_user.id}"),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    try:
        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        entry = soup.find(class_="gmr-download-wrap clearfix")
        hasil = soup.find(class_="title-download").text
        for i in entry.find(class_="list-inline gmr-download-list clearfix"):
            title = i.find("a").text
            link = i.find("a")["href"]
            hasil += f"\n{title}\n{link}\n"
    except Exception as err:
        await editPesan(callback_query.message, f"ERROR: {err}", reply_markup=keyboard)
        return
    await editPesan(callback_query.message, f"<b>Scrape result from</b> <code>{link}</code>:\n\n{hasil}", reply_markup=keyboard)

@app.on_callback_query(filters.create(lambda _, __, query: 'lendriveextract#' in query.data))
async def lendrive_dl(_, callback_query):
    if callback_query.from_user.id != int(callback_query.data.split('#')[3]):
        return await callback_query.answer("Not yours..", True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split('#')[4])
    CurrentPage = int(callback_query.data.split('#')[1])
    try:
        link = SCRAP_DICT[message_id][0][CurrentPage-1][idlink-1].get("link")
    except KeyError:
        return await callback_query.answer("Invalid callback data, please send CMD again..")

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton("↩️ Back", f"page_lendrive#{CurrentPage}#{message_id}#{callback_query.from_user.id}"),
        InlineButton("❌ Close", f"close#{callback_query.from_user.id}")
    )
    try:
        hmm = await http.get(link, headers=headers)
        q = BeautifulSoup(hmm.text, "lxml")
        j = q.findAll("div", class_="soraurlx")
        kl = "<b>#Lendrive Results Download URL:</b>\n\n"
        for i in j:
            if not i.find("a"):
                continue
            kl += f"{i.find('strong')}:\n"
            kl += "".join(f"[ <a href='{a.get('href')}'>{a.text}</a> ]\n" for a in i.findAll("a"))
        await editPesan(callback_query.message, f"<b>Scrape result from</b> <code>{link}</code>:\n\n{kl}", reply_markup=keyboard)
    except Exception as err:
        await editPesan(callback_query.message, f"ERROR: {err}", reply_markup=keyboard)
