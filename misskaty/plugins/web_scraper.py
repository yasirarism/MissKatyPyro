"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @created       2022-12-01 09:12:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import httpx
import logging
import re
import traceback

import cloudscraper
from bs4 import BeautifulSoup
from cachetools import TTLCache
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram.errors import QueryIdInvalid
from pyrogram.types import Message

from database import dbname
from misskaty import app
from misskaty.helper import Cache, Kusonime, fetch, use_chat_lang, post_to_telegraph

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
/samehadaku [query <optional>] - Scrape website data from Samehadaku.
/nodrakor [query <optional>] - Scrape website data from NoDrakor
"""

LOGGER = logging.getLogger("MissKaty")
SCRAP_DICT = Cache(filename="scraper_cache.db", path="cache", in_memory=False)
data_kuso = Cache(filename="kuso_cache.db", path="cache", in_memory=False)
savedict = TTLCache(maxsize=1000, ttl=3600)
webdb = dbname["web"]

web = {
    "yasirapi": "https://yasirapi.eu.org",
    "pahe": "https://pahe.li",
    "savefilm21": "https://savefilm21.skin",
    "melongmovie": "https://melongmovie.site",
    "terbit21": "https://terbit21.gold",
    "lk21": "https://tv1.lk21official.pro",
    "gomov": "https://gomov.bio",
    "movieku": "https://107.152.37.223",
    "kusonime": "https://kusonime.com",
    "lendrive": "https://lendrive.web.id",
    "samehadaku": "https://samehadaku.help",
    "oplovers": "https://oploverz.red",
    "nodrakor": "https://no-drakor.xyz",
}


def split_arr(arr, size: 5):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


# Terbit21 GetData
async def getDataTerbit21(msg, kueri, CurrentPage, strings):
    if not SCRAP_DICT.get(msg.id):
        try:
            if kueri:
                terbitjson = await fetch.get(f"{web['yasirapi']}/terbit21?q={kueri}")
            else:
                terbitjson = await fetch.get(f"{web['yasirapi']}/terbit21")
            terbitjson.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>")
            return None, None
        res = terbitjson.json()
        if not res.get("result"):
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(
            msg.id, [split_arr(res["result"], 6), kueri], timeout=1800
        )
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])

        if kueri:
            TerbitRes = strings("header_with_query").format(web="Terbit21", kueri=kueri)
        else:
            TerbitRes = strings("header_no_query").format(
                web="Terbit21", cmd="terbit21"
            )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            TerbitRes += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('cat_text')}:</b> <code>{i['kategori']}</code>\n"
            TerbitRes += (
                "\n"
                if re.search(r"Complete|Ongoing", i["kategori"])
                else f"<b><a href='{i['dl']}'>{strings('dl_text')}</a></b>\n\n"
            )
        TerbitRes = "".join(i for i in TerbitRes if i not in "[]")
        return TerbitRes, PageLen
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, None


# LK21 GetData
async def getDatalk21(msg, kueri, CurrentPage, strings):
    if not SCRAP_DICT.get(msg.id):
        try:
            if kueri:
                lk21json = await fetch.get(f"{web['yasirapi']}/lk21?q={kueri}")
            else:
                lk21json = await fetch.get(f"{web['yasirapi']}/lk21")
            lk21json.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>")
            return None, None
        res = lk21json.json()
        if not res.get("result"):
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(msg.id, [split_arr(res["result"], 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])

        if kueri:
            lkResult = strings("header_with_query").format(
                web="Layarkaca21", kueri=kueri
            )
        else:
            lkResult = strings("header_no_query").format(web="Layarkaca21", cmd="lk21")
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            lkResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('cat_text')}:</b> <code>{i['kategori']}</code>\n"
            lkResult += (
                "\n"
                if re.search(r"Complete|Ongoing", i["kategori"])
                else f"<b><a href='{i['dl']}'>{strings('dl_text')}</a></b>\n\n"
            )
        lkResult = "".join(i for i in lkResult if i not in "[]")
        return lkResult, PageLen
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, None


# Pahe GetData
async def getDataPahe(msg, kueri, CurrentPage, strings):
    if not SCRAP_DICT.get(msg.id):
        try:
            if kueri:
                pahejson = await fetch.get(f"{web['yasirapi']}/pahe?q={kueri}")
            else:
                pahejson = await fetch.get(f"{web['yasirapi']}/pahe")
            pahejson.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>")
            return None, None
        res = pahejson.json()
        if not res.get("result"):
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(msg.id, [split_arr(res["result"], 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])

        paheResult = (
            strings("header_with_query").format(web="Pahe", kueri=kueri)
            if kueri
            else strings("header_no_query").format(web="Pahe", cmd="pahe")
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            paheResult += (
                f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n\n"
            )
        paheResult = "".join(i for i in paheResult if i not in "[]")
        return paheResult, PageLen
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, None


# Kusonime GetData
async def getDataKuso(msg, kueri, CurrentPage, user, strings):
    if not SCRAP_DICT.get(msg.id):
        kusodata = []
        try:
            data = await fetch.get(
                f"{web['kusonime']}/?s={kueri}", follow_redirects=True
            )
            data.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>", disable_web_page_preview=True)
            return None, 0, None, None
        res = BeautifulSoup(data, "lxml").find_all("h2", {"class": "episodeye"})
        for i in res:
            ress = i.find_all("a")[0]
            title = ress.text
            link = ress["href"]
            kusodata.append({"title": title, "link": link})
        if not kusodata:
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, 0, None, None
        SCRAP_DICT.add(msg.id, [split_arr(kusodata, 10), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn1 = []
        extractbtn2 = []

        kusoResult = (
            strings("header_no_query").format(web="Kusonime", cmd="kusonime")
            if kueri == ""
            else strings("header_with_query").format(web="Kusonime", kueri=kueri)
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            kusoResult += f"<b>{index*6+c}</b>. {i['title']}\n{i['link']}\n\n"
            if c < 6:
                extractbtn1.append(
                    InlineButton(
                        index * 6 + c, f"kusoextract#{CurrentPage}#{c}#{user}#{msg.id}"
                    )
                )
            else:
                extractbtn2.append(
                    InlineButton(
                        index * 6 + c, f"kusoextract#{CurrentPage}#{c}#{user}#{msg.id}"
                    )
                )
        kusoResult = "".join(i for i in kusoResult if i not in "[]")
        return kusoResult, PageLen, extractbtn1, extractbtn2
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, 0, None, None


# Movieku GetData
async def getDataMovieku(msg, kueri, CurrentPage, strings):
    if not SCRAP_DICT.get(msg.id):
        moviekudata = []
        try:
            data = await fetch.get(
                f"{web['movieku']}/?s={kueri}", follow_redirects=True
            )
            data.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>")
            return None, None
        r = BeautifulSoup(data, "lxml")
        res = r.find_all(class_="bx")
        for i in res:
            judul = i.find_all("a")[0]["title"]
            link = i.find_all("a")[0]["href"]
            typ = i.find(class_="overlay").text
            typee = typ.strip() if typ.strip() != "" else "~"
            moviekudata.append({"judul": judul, "link": link, "type": typee})
        if not moviekudata:
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(msg.id, [split_arr(moviekudata, 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])

        moviekuResult = (
            strings("header_no_query").format(web="Movieku", cmd="movieku")
            if kueri == ""
            else strings("header_with_query").format(web="Movieku", kueri=kueri)
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            moviekuResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('quality')}/Status:</b> {i['type']}\n<b>Extract:</b> <code>/movieku_scrap {i['link']}</code>\n\n"
        moviekuResult = "".join(i for i in moviekuResult if i not in "[]")
        return moviekuResult, PageLen
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, None


# NoDrakor GetData
async def getDataNodrakor(msg, kueri, CurrentPage, user, strings):
    if not SCRAP_DICT.get(msg.id):
        nodrakordata = []
        try:
            data = await fetch.get(
                f"{web['nodrakor']}/?s={kueri}", follow_redirects=True,
            )
            data.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", disable_web_page_preview=True)
            return None, 0, None
        text = BeautifulSoup(data, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Tidak Ditemukan" in entry[0].text:
            if not kueri:
                await msg.edit_msg(strings("no_result"), del_in=5)
            else:
                await msg.edit_msg(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            nodrakordata.append({"judul": judul, "link": link, "genre": genre})
        SCRAP_DICT.add(msg.id, [split_arr(nodrakordata, 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []
        nodrakorResult = (
            strings("header_no_query").format(web="NoDrakor", cmd="nodrakor")
            if kueri == ""
            else strings("header_with_query").format(web="NoDrakor", kueri=kueri)
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            nodrakorResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> {i['genre']}\n\n"
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"nodrakorextract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
        nodrakorResult = "".join(i for i in nodrakorResult if i not in "[]")
        return nodrakorResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, 0, None


# Savefilm21 GetData
async def getDataSavefilm21(msg, kueri, CurrentPage, user, strings):
    if not SCRAP_DICT.get(msg.id):
        sfdata = []
        try:
            data = await fetch.get(
                f"{web['savefilm21']}/?s={kueri}", follow_redirects=True,
            )
            data.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", disable_web_page_preview=True)
            return None, 0, None
        text = BeautifulSoup(data, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Tidak Ditemukan" in entry[0].text:
            if not kueri:
                await msg.edit_msg(strings("no_result"), del_in=5)
            else:
                await msg.edit_msg(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            sfdata.append({"judul": judul, "link": link, "genre": genre})
        SCRAP_DICT.add(msg.id, [split_arr(sfdata, 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []
        sfResult = (
            strings("header_no_query").format(web="Savefilm21", cmd="savefilm21")
            if kueri == ""
            else strings("header_with_query").format(web="Savefilm21", kueri=kueri)
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            sfResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> {i['genre']}\n\n"
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"sf21extract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
        sfResult = "".join(i for i in sfResult if i not in "[]")
        return sfResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, 0, None


# Lendrive GetData
async def getDataLendrive(msg, kueri, CurrentPage, user, strings):
    if not SCRAP_DICT.get(msg.id):
        try:
            if kueri:
                data = await fetch.get(
                    f"{web['lendrive']}/?s={kueri}", follow_redirects=True,
                )
            else:
                data = await fetch.get(web["lendrive"], follow_redirects=True)
            data.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>", disable_web_page_preview=True)
            return None, 0, None
        res = BeautifulSoup(data, "lxml")
        lenddata = []
        for o in res.find_all(class_="bsx"):
            title = o.find("a")["title"]
            link = o.find("a")["href"]
            status = (
                o.find(class_="epx").text
                if o.find(class_="epx")
                else "Not Provided by BOT"
            )
            kualitas = (
                o.find(class_="typez TV").text
                if o.find(class_="typez TV")
                else o.find(class_="typez BD")
            )
            lenddata.append(
                {"judul": title, "link": link, "quality": kualitas or "N/A", "status": status}
            )
        if not lenddata:
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, 0, None
        savedict[msg.id] = [split_arr(lenddata, 6), kueri]
    try:
        index = int(CurrentPage - 1)
        PageLen = len(savedict[msg.id][0])
        extractbtn = []

        lenddataResult = (
            strings("header_no_query").format(web="Lendrive", cmd="lendrive")
            if kueri == ""
            else strings("header_with_query").format(web="Lendrive", kueri=kueri)
        )
        for c, i in enumerate(savedict[msg.id][0][index], start=1):
            lenddataResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('quality')}:</b> {i['quality']}\n<b>Status:</b> {i['status']}\n\n"
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"lendriveextract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
        lenddataResult = "".join(i for i in lenddataResult if i not in "[]")
        return lenddataResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, 0, None


# MelongMovie GetData
async def getDataMelong(msg, kueri, CurrentPage, user, strings):
    if not SCRAP_DICT.get(msg.id):
        try:
            data = await fetch.get(
                f"{web['melongmovie']}/?s={kueri}", follow_redirects=True,
            )
            data.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", disable_web_page_preview=True)
            return None, 0, None
        bs4 = BeautifulSoup(data, "lxml")
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
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, 0, None
        SCRAP_DICT.add(msg.id, [split_arr(melongdata, 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []

        melongResult = (
            strings("header_no_query").format(web="Melongmovie", cmd="melongmovie")
            if kueri == ""
            else strings("header_with_query").format(web="Melongmovie", kueri=kueri)
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            melongResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('quality')}:</b> {i['quality']}\n\n"
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"melongextract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
        melongResult = "".join(i for i in melongResult if i not in "[]")
        return melongResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, 0, None


# GoMov GetData
async def getDataGomov(msg, kueri, CurrentPage, user, strings):
    if not SCRAP_DICT.get(msg.id):
        try:
            gomovv = await fetch.get(
                f"{web['gomov']}/?s={kueri}", follow_redirects=True
            )
            gomovv.raise_for_status()
        except httpx.HTTPError as exc:
            await msg.edit_msg(f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>", disable_web_page_preview=True)
            return None, 0, None
        text = BeautifulSoup(gomovv, "lxml")
        entry = text.find_all(class_="entry-header")
        if entry[0].text.strip() == "Nothing Found":
            if not kueri:
                await msg.edit_msg(strings("no_result"), del_in=5)
            else:
                await msg.edit_msg(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        else:
            data = []
            for i in entry:
                genre = i.find(class_="gmr-movie-on").text
                genre = f"{genre}" if genre != "" else "N/A"
                judul = i.find(class_="entry-title").find("a").text
                link = i.find(class_="entry-title").find("a").get("href")
                data.append({"judul": judul, "link": link, "genre": genre})
            SCRAP_DICT.add(msg.id, [split_arr(data, 6), kueri], timeout=1800)
    try:
        index = int(CurrentPage - 1)
        PageLen = len(SCRAP_DICT[msg.id][0])
        extractbtn = []

        gomovResult = (
            strings("header_with_query").format(web="GoMov", kueri=kueri)
            if kueri
            else strings("header_no_query").format(web="GoMov", cmd="gomov")
        )
        for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
            gomovResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n\n"
            if not re.search(r"Series", i["genre"]):
                extractbtn.append(
                    InlineButton(
                        index * 6 + c, f"gomovextract#{CurrentPage}#{c}#{user}#{msg.id}"
                    )
                )
        gomovResult += strings("unsupport_dl_btn")
        gomovResult = "".join(i for i in gomovResult if i not in "[]")
        return gomovResult, PageLen, extractbtn
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, 0, None


# getData samehada
async def getSame(msg, query, current_page, strings):
    if not SCRAP_DICT.get(msg.id):
        cfse = cloudscraper.create_scraper()
        if query:
            data = cfse.get(f"{web['samehadaku']}/?s={query}")
        else:
            data = cfse.get(web["samehadaku"])
        if data.status_code != 200:
            await msg.edit_msg(strings("err_getweb").format(err=data.status_code))
            return None, None
        res = BeautifulSoup(data.text, "lxml").find_all(class_="animposx")
        sdata = []
        for i in res:
            url = i.find("a")["href"]
            title = i.find("a")["title"]
            sta = (
                i.find(class_="type TV").text if i.find(class_="type TV") else "Ongoing"
            )
            rate = i.find(class_="score")
            sdata.append({"url": url, "title": title, "sta": sta, "rate": rate})
        if not sdata:
            await msg.edit_msg(strings("no_result"), del_in=5)
            return None, None
        savedict[msg.id] = [split_arr(sdata, 10), query]
    try:
        index = int(current_page - 1)
        PageLen = len(savedict[msg.id][0])
        sameresult = "".join(
            f"<b>{index * 6 + c}. <a href='{i['url']}'>{i['title']}</a>\n<b>Status:</b> {i['sta']}\n</b>Rating:</b> {i['rate']}\n\n"
            for c, i in enumerate(savedict[msg.id][0][index], start=1)
        )
        sameresult = "".join(i for i in sameresult if i not in "[]")
        return sameresult, PageLen
    except (IndexError, KeyError):
        await msg.edit_msg(strings("no_result"), del_in=5)
        return None, None


# SameHada CMD
@app.on_cmd("samehadaku", no_channel=True)
@use_chat_lang()
async def same_search(_, msg, strings):
    query = msg.text.split(maxsplit=1)[1] if len(msg.command) > 1 else None
    bmsg = await msg.reply_msg(strings("get_data"), quote=True)
    sameres, PageLen = await getSame(bmsg, query, 1, strings)
    if not sameres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen, 1, "page_same#{number}" + f"#{bmsg.id}#{msg.from_user.id}"
    )
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{msg.from_user.id}"))
    await bmsg.edit_msg(sameres, disable_web_page_preview=True, reply_markup=keyboard)


# Terbit21 CMD
@app.on_cmd("terbit21", no_channel=True)
@use_chat_lang()
async def terbit21_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = None
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    terbitres, PageLen = await getDataTerbit21(pesan, kueri, CurrentPage, strings)
    if not terbitres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_terbit21#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(
        terbitres, disable_web_page_preview=True, reply_markup=keyboard
    )


# LK21 CMD
@app.on_cmd("lk21", no_channel=True)
@use_chat_lang()
async def lk21_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = None
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    lkres, PageLen = await getDatalk21(pesan, kueri, CurrentPage, strings)
    if not lkres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_lk21#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(lkres, disable_web_page_preview=True, reply_markup=keyboard)


# Pahe CMD
@app.on_cmd("pahe", no_channel=True)
@use_chat_lang()
async def pahe_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    paheres, PageLen = await getDataPahe(pesan, kueri, CurrentPage, strings)
    if not paheres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_pahe#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(paheres, disable_web_page_preview=True, reply_markup=keyboard)


# Gomov CMD
@app.on_cmd("gomov", no_channel=True)
@use_chat_lang()
async def gomov_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    gomovres, PageLen, btn = await getDataGomov(
        pesan, kueri, CurrentPage, message.from_user.id, strings
    )
    if not gomovres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_gomov#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=message.from_user.id))
    keyboard.row(*btn)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(gomovres, disable_web_page_preview=True, reply_markup=keyboard)


# MelongMovie CMD
@app.on_cmd("melongmovie", no_channel=True)
@use_chat_lang()
async def melong_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    melongres, PageLen, btn = await getDataMelong(
        pesan, kueri, CurrentPage, message.from_user.id, strings
    )
    if not melongres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_melong#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=message.from_user.id))
    keyboard.row(*btn)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    try:
        await pesan.edit_msg(
            melongres, disable_web_page_preview=True, reply_markup=keyboard
        )
    except Exception as err:
        await pesan.edit_msg(
            f"<b>ERROR:</b> {err}", disable_web_page_preview=True, reply_markup=keyboard
        )


# Savefilm21 CMD
@app.on_cmd("savefilm21", no_channel=True)
@use_chat_lang()
async def savefilm_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    savefilmres, PageLen, btn = await getDataSavefilm21(
        pesan, kueri, CurrentPage, message.from_user.id, strings
    )
    if not savefilmres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_sf21#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=message.from_user.id))
    keyboard.row(*btn)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(
        savefilmres, disable_web_page_preview=True, reply_markup=keyboard
    )


# NoDrakor CMD
@app.on_cmd("nodrakor", no_channel=True)
@use_chat_lang()
async def nodrakor_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    nodrakorres, PageLen, btn = await getDataNodrakor(
        pesan, kueri, CurrentPage, message.from_user.id, strings
    )
    if not nodrakorres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_nodrakor#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=message.from_user.id))
    keyboard.row(*btn)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(
        nodrakorres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Kusonime CMD
@app.on_cmd("kusonime", no_channel=True)
@use_chat_lang()
async def kusonime_s(_, message, strings):
    kueri = " ".join(message.command[1:])
    if not kueri:
        kueri = ""
    pesan = await message.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    kusores, PageLen, btn1, btn2 = await getDataKuso(
        pesan, kueri, CurrentPage, message.from_user.id, strings
    )
    if not kusores:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_kuso#{number}" + f"#{pesan.id}#{message.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=message.from_user.id))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit_msg(kusores, disable_web_page_preview=True, reply_markup=keyboard)


# Lendrive CMD
@app.on_cmd("lendrive", no_channel=True)
@use_chat_lang()
async def lendrive_s(_, ctx: Message, strings):
    kueri = ctx.input
    if not kueri:
        kueri = ""
    pesan = await ctx.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    lendres, PageLen, btn = await getDataLendrive(
        pesan, kueri, CurrentPage, ctx.from_user.id, strings
    )
    if not lendres:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_lendrive#{number}" + f"#{pesan.id}#{ctx.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=ctx.from_user.id))
    keyboard.row(*btn)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{ctx.from_user.id}"))
    await pesan.edit_msg(lendres, disable_web_page_preview=True, reply_markup=keyboard)


# Movieku CMD
@app.on_cmd("movieku", no_channel=True)
@use_chat_lang()
async def movieku_s(_, ctx: Message, strings):
    kueri = ctx.input
    if not kueri:
        kueri = ""
    pesan = await ctx.reply_msg(strings("get_data"), quote=True)
    CurrentPage = 1
    moviekures, PageLen = await getDataMovieku(pesan, kueri, CurrentPage, strings)
    if not moviekures:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_movieku#{number}" + f"#{pesan.id}#{ctx.from_user.id}",
    )
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{ctx.from_user.id}"))
    await pesan.edit_msg(
        moviekures, disable_web_page_preview=True, reply_markup=keyboard
    )


# Savefillm21 Page Callback
@app.on_cb("page_sf21#")
@use_chat_lang()
async def sf21page_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except (IndexError, ValueError):  # Gatau napa err ini
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))
    except QueryIdInvalid:
        return

    try:
        savefilmres, PageLen, btn = await getDataSavefilm21(
            callback_query.message,
            kueri,
            CurrentPage,
            callback_query.from_user.id,
            strings,
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_sf21#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=callback_query.from_user.id))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        savefilmres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Savefillm21 Page Callback
@app.on_cb("page_nodrakor#")
@use_chat_lang()
async def nodrakorpage_cb(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except (IndexError, ValueError):
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))
    except QueryIdInvalid:
        return

    try:
        nodrakorres, PageLen, btn = await getDataNodrakor(
            callback_query.message,
            kueri,
            CurrentPage,
            callback_query.from_user.id,
            strings,
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_nodrakor#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=callback_query.from_user.id))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        nodrakorres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Kuso Page Callback
@app.on_cb("page_kuso#")
@use_chat_lang()
async def kusopage_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        kusores, PageLen, btn1, btn2 = await getDataKuso(
            callback_query.message,
            kueri,
            CurrentPage,
            callback_query.from_user.id,
            strings,
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_kuso#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=callback_query.from_user.id))
    keyboard.row(*btn1)
    if btn2:
        keyboard.row(*btn2)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        kusores, disable_web_page_preview=True, reply_markup=keyboard
    )


# Lendrive Page Callback
@app.on_cb("page_lendrive#")
@use_chat_lang()
async def lendrivepage_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = savedict[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        lendres, PageLen, btn = await getDataLendrive(
            callback_query.message,
            kueri,
            CurrentPage,
            callback_query.from_user.id,
            strings,
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_lendrive#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=callback_query.from_user.id))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        lendres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Movieku Page Callback
@app.on_cb("page_movieku#")
@use_chat_lang()
async def moviekupage_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"), True)

    try:
        moviekures, PageLen = await getDataMovieku(
            callback_query.message, kueri, CurrentPage, strings
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_movieku#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        moviekures, disable_web_page_preview=True, reply_markup=keyboard
    )


# Samehada Page Callback
@app.on_cb("page_same#")
@use_chat_lang()
async def samepg(_, query, strings):
    try:
        _, current_page, _id, user_id = query.data.split("#")
        if int(user_id) != query.from_user.id:
            return await query.answer(strings("unauth"), True)
        lquery = savedict[int(_id)][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await query.message.edit_msg(strings("invalid_cb"))
    try:
        sameres, PageLen = await getSame(
            query.message, lquery, int(current_page), strings
        )
    except TypeError:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        int(current_page),
        "page_same#{number}" + f"#{_id}#{query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{query.from_user.id}"))
    await query.message.edit_msg(
        sameres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Terbit21 Page Callback
@app.on_cb("page_terbit21#")
@use_chat_lang()
async def terbit21page_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        terbitres, PageLen = await getDataTerbit21(
            callback_query.message, kueri, CurrentPage, strings
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_terbit21#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        terbitres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Page Callback Melong
@app.on_cb("page_melong#")
@use_chat_lang()
async def melongpage_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        terbitres, PageLen, btn = await getDataMelong(
            callback_query.message,
            kueri,
            CurrentPage,
            callback_query.from_user.id,
            strings,
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_melong#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=callback_query.from_user.id))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        terbitres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Lk21 Page Callback
@app.on_cb("page_lk21#")
@use_chat_lang()
async def lk21page_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        lkres, PageLen = await getDatalk21(
            callback_query.message, kueri, CurrentPage, strings
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_lk21#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        lkres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Pahe Page Callback
@app.on_cb("page_pahe#")
@use_chat_lang()
async def pahepage_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        lkres, PageLen = await getDataPahe(
            callback_query.message, kueri, CurrentPage, strings
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_pahe#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        lkres, disable_web_page_preview=True, reply_markup=keyboard
    )


# Gomov Page Callback
@app.on_cb("page_gomov#")
@use_chat_lang()
async def gomovpage_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    try:
        gomovres, PageLen, btn = await getDataGomov(
            callback_query.message,
            kueri,
            CurrentPage,
            callback_query.from_user.id,
            strings,
        )
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        "page_gomov#{number}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    keyboard.row(InlineButton(strings("ex_data"), user_id=callback_query.from_user.id))
    keyboard.row(*btn)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit_msg(
        gomovres, disable_web_page_preview=True, reply_markup=keyboard
    )


### Scrape DDL Link From Web ###
# Kusonime DDL
@app.on_cb("kusoextract#")
@use_chat_lang()
async def kusonime_scrap(client, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        idlink = int(callback_query.data.split("#")[2])
        message_id = int(callback_query.data.split("#")[4])
        CurrentPage = int(callback_query.data.split("#")[1])
        link = SCRAP_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    kuso = Kusonime()
    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"page_kuso#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    try:
        init_url = data_kuso.get(link, False)
        if init_url:
            await callback_query.message.edit_msg(init_url.get("ph_url"), reply_markup=keyboard)
        tgh = await kuso.telegraph(link, client.me.username)
        data_kuso[link] = {"ph_url": tgh}
        return await callback_query.message.edit_msg(tgh, reply_markup=keyboard)
    except Exception as e:
        LOGGER.error(f"clases: {e.__class__}, moduleName: {e.__class__.__name__}")
        if str(e).startswith("ERROR"):
            return await callback_query.message.edit_msg(e, reply_markup=keyboard)


# Savefilm21 DDL
@app.on_cb("sf21extract#")
@use_chat_lang()
async def savefilm21_scrap(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        idlink = int(callback_query.data.split("#")[2])
        message_id = int(callback_query.data.split("#")[4])
        CurrentPage = int(callback_query.data.split("#")[1])
        link = SCRAP_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"page_sf21#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    try:
        html = await fetch.get(link)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="button button-shadow")
        res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
        await callback_query.message.edit_msg(
            strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
        )
    except httpx.HTTPError as exc:
        await callback_query.message.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", reply_markup=keyboard)
    except Exception as err:
        await callback_query.message.edit_msg(f"ERROR: {err}", reply_markup=keyboard)


# NoDrakor DDL
@app.on_cb("nodrakorextract#")
@use_chat_lang()
async def nodrakorddl_scrap(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        idlink = int(callback_query.data.split("#")[2])
        message_id = int(callback_query.data.split("#")[4])
        CurrentPage = int(callback_query.data.split("#")[1])
        link = SCRAP_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"page_nodrakor#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    try:
        html = await fetch.get(link)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, "lxml")
        if "/tv/" in link:
            result = soup.find("div", {"entry-content entry-content-single"}).find_all("p")
            msg = ""
            for i in result:
                msg += str(f"{i}\n")
            link = await post_to_telegraph(False, "MissKaty NoDrakor", msg)
            return await callback_query.message.edit_msg(
                strings("res_scrape").format(link=link, kl=link), reply_markup=keyboard
            )
        res = soup.find_all(class_="button button-shadow")
        res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
        if len(res) > 3500:
            link = await post_to_telegraph(False, "MissKaty NoDrakor", res)
            return await callback_query.message.edit_msg(
                strings("res_scrape").format(link=link, kl=link), reply_markup=keyboard
            )
        await callback_query.message.edit_msg(
            strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
        )
    except httpx.HTTPError as exc:
        await callback_query.message.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", reply_markup=keyboard)
    except Exception as err:
        await callback_query.message.edit_msg(f"ERROR: {err}", reply_markup=keyboard)


# Scrape Link Download Movieku.CC
@app.on_cmd("movieku_scrap")
@use_chat_lang()
async def muviku_scrap(_, message, strings):
    try:
        link = message.text.split(maxsplit=1)[1]
        html = await fetch.get(link)
        html.raise_for_status()
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
            return await message.reply(strings("no_result"))
        res = "".join(f"<b>Host: {i['kualitas']}</b>\n{i['link']}\n\n" for i in data)
        await message.reply(res)
    except IndexError:
        return await message.reply(
            strings("invalid_cmd_scrape").format(cmd=message.command[0])
        )
    except httpx.HTTPError as exc:
        await message.reply(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>")
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


# Scrape DDL Link Melongmovie
@app.on_cb("melongextract#")
@use_chat_lang()
async def melong_scrap(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        idlink = int(callback_query.data.split("#")[2])
        message_id = int(callback_query.data.split("#")[4])
        CurrentPage = int(callback_query.data.split("#")[1])
        link = SCRAP_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"page_melong#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    try:
        html = await fetch.get(link)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, "lxml")
        rep = ""
        for ep in soup.findAll(text=re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
            hardsub = ep.findPrevious("div")
            softsub = ep.findNext("div")
            rep += f"{hardsub}\n{softsub}"
        await callback_query.message.edit_msg(
            strings("res_scrape").format(link=link, kl=rep), reply_markup=keyboard
        )
    except httpx.HTTPError as exc:
        await callback_query.message.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", reply_markup=keyboard)
    except Exception as err:
        await callback_query.message.edit_msg(f"ERROR: {err}", reply_markup=keyboard)


# Scrape DDL Link Gomov
@app.on_cb("gomovextract#")
@use_chat_lang()
async def gomov_dl(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        idlink = int(callback_query.data.split("#")[2])
        message_id = int(callback_query.data.split("#")[4])
        CurrentPage = int(callback_query.data.split("#")[1])
        link = SCRAP_DICT[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except QueryIdInvalid:
        return
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"page_gomov#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    try:
        html = await fetch.get(link)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, "lxml")
        entry = soup.find(class_="gmr-download-wrap clearfix")
        hasil = soup.find(class_="title-download").text
        for i in entry.find(class_="list-inline gmr-download-list clearfix"):
            title = i.find("a").text
            ddl = i.find("a")["href"]
            hasil += f"\n{title}\n{ddl}\n"
        await callback_query.message.edit_msg(
            strings("res_scrape").format(link=link, kl=hasil), reply_markup=keyboard
        )
    except httpx.HTTPError as exc:
        await callback_query.message.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", reply_markup=keyboard)
    except Exception as err:
        await callback_query.message.edit_msg(f"ERROR: {err}", reply_markup=keyboard)


@app.on_cb("lendriveextract#")
@use_chat_lang()
async def lendrive_dl(_, callback_query, strings):
    if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
        return await callback_query.answer(strings("unauth"), True)
    idlink = int(callback_query.data.split("#")[2])
    message_id = int(callback_query.data.split("#")[4])
    CurrentPage = int(callback_query.data.split("#")[1])
    try:
        link = savedict[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except KeyError:
        return await callback_query.message.edit_msg(strings("invalid_cb"))

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"page_lendrive#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    try:
        hmm = await fetch.get(link)
        hmm.raise_for_status()
        q = BeautifulSoup(hmm.text, "lxml")
        j = q.findAll("div", class_="soraurlx")
        kl = ""
        for i in j:
            if not i.find("a"):
                continue
            kl += f"{i.find('strong')}:\n"
            kl += "".join(
                f"[ <a href='{a.get('href')}'>{a.text}</a> ]\n" for a in i.findAll("a")
            )
        await callback_query.message.edit_msg(
            strings("res_scrape").format(link=link, kl=kl), reply_markup=keyboard
        )
    except httpx.HTTPError as exc:
        await callback_query.message.edit_msg(f"HTTP Exception for {exc.request.url} - <code>{exc}</code>", reply_markup=keyboard)
    except Exception as err:
        await callback_query.message.edit_msg(f"ERROR: {err}", reply_markup=keyboard)
