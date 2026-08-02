"""
* @author        yasir <yasiramunandar@gmail.com>
* @created       2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

import contextlib
import logging
import re
import sys
from html import escape
from urllib.parse import quote_plus, urljoin

import cloudscraper
import httpx
from bs4 import BeautifulSoup
from cachetools import TTLCache
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import filters
from pyrogram import types as pyro_types
from pyrogram.errors import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database import dbname
from misskaty import app
from misskaty.helper import (
    Cache,
    Kusonime,
    fetch,
    post_to_telegraph,
    resp_get,
    run_sync,
    use_chat_lang,
)
from misskaty.vars import OWNER_ID

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
/klikxxi [query <optional>] - Scrape website data from Klikxxi aka GoMov.
/samehadaku [query <optional>] - Scrape website data from Samehadaku.
/nodrakor [query <optional>] - Scrape website data from NoDrakor
/nunadrama [query <optional>] - Scrape website data from NunaDrama
/dutamovie [query <optional>] - Scrape website data from DutaMovie
/pusatfilm [query <optional>] - Scrape website data from Pusatfilm21
/oppaweb [query <optional>] - Scrape website data from OppaWeb.
/webdomain - Edit scraper domains via interactive buttons (OWNER only).
"""

LOGGER = logging.getLogger("MissKaty")
SCRAP_DICT = Cache(filename="scraper_cache.db", path="cache", in_memory=False)
data_kuso = Cache(filename="kuso_cache.db", path="cache", in_memory=False)
savedict = TTLCache(maxsize=1000, ttl=3600)
webdb = dbname["web"]

DEFAULT_WEB = {
    "yasirapi": "https://yasirapi.eu.org",
    "yasirapi_v2": "https://v2.yasirapi.eu.org",
    "pahe": "pahe.ink",
    "savefilm21": "https://new13.savefilm21info.com",
    "melongmovie": "https://tv12.melongmovies.com",
    "terbit21": "https://terbit21official.site",
    "lk21": "https://tv12.lk21official.cc",
    "gomov": "https://klikxxi.com",
    "movieku": "https://movieku.fit",
    "kusonime": "https://kusonime.com",
    "lendrive": "https://lendrive.web.id",
    "samehadaku": "https://samehadaku.help",
    "oplovers": "https://oploverz.red",
    "nodrakor": "https://no-drakor.xyz",
    "nunadrama": "https://s1.nunadrama.live",
    "dutamovie": "https://yborfilmfestival.com",
    "pusatfilm": "http://217.76.53.139",
    "oppaweb": "http://45.11.57.199",
}
web = DEFAULT_WEB.copy()
WEB_CONFIG_LOADED = False


async def ensure_web_config():
    global WEB_CONFIG_LOADED
    if WEB_CONFIG_LOADED:
        return
    web.clear()
    web.update(DEFAULT_WEB)
    doc = await webdb.find_one({"_id": "domains"})
    if doc and doc.get("values"):
        web.update(doc["values"])
        WEB_CONFIG_LOADED = True
        return
    async for entry in webdb.find({}):
        for key, value in entry.items():
            if key == "_id":
                continue
            web[key] = value
    WEB_CONFIG_LOADED = True


async def save_web_config():
    await webdb.update_one(
        {"_id": "domains"}, {"$set": {"values": web}}, upsert=True
    )


def build_web_buttons(uid: int):
    rows = []
    row = []
    keys = list(sorted(DEFAULT_WEB)) + sorted(set(web) - set(DEFAULT_WEB))
    for index, key in enumerate(keys, start=1):
        row.append(InlineKeyboardButton(key, callback_data=f"webdomain#{key}#{uid}"))
        if index % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ Close", callback_data=f"close#{uid}")])
    return InlineKeyboardMarkup(rows)


def build_web_domain_menu(uid: int, key: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👁 View", callback_data=f"webdomainview#{key}#{uid}"
                ),
                InlineKeyboardButton(
                    "✏️ Edit", callback_data=f"webdomainedit#{key}#{uid}"
                ),
            ],
            [InlineKeyboardButton("↩️ Back", callback_data=f"webdomainback#{uid}")],
            [InlineKeyboardButton("❌ Close", callback_data=f"close#{uid}")],
        ]
    )


@app.on_cmd("webdomain", no_channel=True)
@use_chat_lang()
async def webdomain_cmd(_, message, strings):
    if not message.from_user:
        return
    if message.from_user.id != OWNER_ID:
        return await message.reply("⚠️ Access Denied!", del_in=5)
    await ensure_web_config()
    text = "<b>Web Domain Editor</b>\nPilih domain yang ingin kamu ubah."
    keyboard = build_web_buttons(message.from_user.id)
    await message.reply(text, reply_markup=keyboard)


@app.on_cb("webdomain#")
@use_chat_lang()
async def webdomain_edit(_, query, strings):
    _, key, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("⚠️ Access Denied!", True)
    await ensure_web_config()
    if key not in web and key in DEFAULT_WEB:
        web[key] = DEFAULT_WEB[key]
    if key not in web:
        return await query.answer("⚠️ Domain tidak ditemukan.", True)
    text = (
        "<b>Web Domain Editor</b>\n"
        f"<b>Nama:</b> <code>{key}</code>\n"
        f"<b>Saat ini:</b> <code>{web[key]}</code>\n\n"
        "Pilih aksi di bawah."
    )
    await query.message.edit(
        text, reply_markup=build_web_domain_menu(query.from_user.id, key)
    )


@app.on_cb("webdomainview#")
@use_chat_lang()
async def webdomain_view(_, query, strings):
    _, key, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("⚠️ Access Denied!", True)
    await ensure_web_config()
    if key not in web and key in DEFAULT_WEB:
        web[key] = DEFAULT_WEB[key]
    if key not in web:
        return await query.answer("⚠️ Domain tidak ditemukan.", True)
    text = (
        "<b>Web Domain</b>\n"
        f"<b>Nama:</b> <code>{key}</code>\n"
        f"<b>Domain:</b> <code>{web[key]}</code>"
    )
    await query.message.edit(
        text, reply_markup=build_web_domain_menu(query.from_user.id, key)
    )


@app.on_cb("webdomainedit#")
@use_chat_lang()
async def webdomain_edit_value(_, query, strings):
    _, key, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("⚠️ Access Denied!", True)
    await ensure_web_config()
    if key not in web and key in DEFAULT_WEB:
        web[key] = DEFAULT_WEB[key]
    if key not in web:
        return await query.answer("⚠️ Domain tidak ditemukan.", True)
    await query.message.edit(
        f"Kirim domain baru untuk <b>{key}</b>.\n"
        f"Saat ini: <code>{web[key]}</code>\n"
        "Ketik <code>/cancel</code> untuk batal."
    )
    try:
        response = await query.message.ask(
            "Masukkan domain baru:",
            filters=filters.text,
            timeout=60,
            from_user_id=query.from_user.id,
        )
    except Exception:
        return await query.message.edit("⚠️ Waktu habis.")
    if response.text.strip().lower() == "/cancel":
        with contextlib.suppress(Exception):
            await response.delete()
        with contextlib.suppress(Exception):
            if response.reply_to_message:
                await response.reply_to_message.delete()
        return await query.message.edit(
            "Dibatalkan.", reply_markup=build_web_buttons(query.from_user.id)
        )
    web[key] = response.text.strip()
    await save_web_config()
    with contextlib.suppress(Exception):
        await response.delete()
    with contextlib.suppress(Exception):
        if response.reply_to_message:
            await response.reply_to_message.delete()
    await query.message.edit(
        f"✅ Domain <b>{key}</b> diperbarui menjadi:\n<code>{web[key]}</code>",
        reply_markup=build_web_domain_menu(query.from_user.id, key),
    )


@app.on_cb("webdomainback#")
@use_chat_lang()
async def webdomain_back(_, query, strings):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("⚠️ Access Denied!", True)
    await ensure_web_config()
    text = "<b>Web Domain Editor</b>\nPilih domain yang ingin kamu ubah."
    keyboard = build_web_buttons(query.from_user.id)
    await query.message.edit(text, reply_markup=keyboard)


def split_arr(arr, size: 5):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


OPPAWEB_MAX_PAGES = 5
OPPAWEB_COOKIES = {"user_is_human": "true"}
OPPAWEB_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
}


def oppaweb_url(path: str = ""):
    base_url = web["oppaweb"].rstrip("/")
    if not path:
        return base_url
    return f"{base_url}/{path.lstrip('/')}"


def oppaweb_search_url(kueri: str, page: int):
    if kueri:
        query = quote_plus(kueri)
        if page == 1:
            return oppaweb_url(f"?s={query}")
        return oppaweb_url(f"page/{page}/?s={query}")
    if page == 1:
        return oppaweb_url()
    return oppaweb_url(f"page/{page}/")


def oppaweb_request_headers(referer=None):
    headers = OPPAWEB_HEADERS.copy()
    if referer:
        headers["Referer"] = referer
    return headers


def parse_oppaweb_search(html: str):
    soup = BeautifulSoup(html, "lxml")
    results = []
    for article in soup.find_all("article", class_="bs"):
        title_elem = article.find("h2", itemprop="headline")
        link_elem = article.find("a", itemprop="url")
        if not link_elem or not link_elem.get("href"):
            continue
        type_elem = article.find("div", class_="typez")
        status_elem = article.find("span", class_="epx")
        sub_elem = article.find("span", class_="sb")
        results.append(
            {
                "judul": title_elem.text.strip() if title_elem else "Judul tidak diketahui",
                "link": urljoin(oppaweb_url(), link_elem["href"]),
                "type": type_elem.text.strip() if type_elem else "-",
                "status": status_elem.text.strip() if status_elem else "-",
                "subtitle": sub_elem.text.strip() if sub_elem else "-",
            }
        )
    pagination = soup.find("div", class_="pagination")
    has_next = bool(pagination and pagination.find("a", class_="next"))
    return results, has_next


def clean_oppaweb_text(element):
    return " ".join(element.stripped_strings) if element else ""


def parse_oppaweb_episode_link(html: str):
    soup = BeautifulSoup(html, "lxml")
    episode_link = soup.select_one(".epcheck .eplister li a[href]")
    if not episode_link:
        episode_link = soup.select_one(".epcheck a[href]")
    if not episode_link:
        episode_link = soup.select_one(".bixbox.episodedl a[href]")
    return urljoin(oppaweb_url(), episode_link["href"]) if episode_link else None


def parse_oppaweb_synopsis(soup):
    for selector in (
        ".bixbox.synp .entry-content",
        ".entry-content[itemprop='description']",
        ".desc.mindes",
        ".desc",
        ".mindesc",
    ):
        synopsis = clean_oppaweb_text(soup.select_one(selector))
        if synopsis:
            return synopsis
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        return meta_desc["content"].strip()
    return "Sinopsis tidak ditemukan"


def parse_oppaweb_detail(html: str):
    soup = BeautifulSoup(html, "lxml")
    title_elem = soup.find("h1", class_="entry-title")
    rating_elem = soup.find("div", class_="rating")
    synopsis = parse_oppaweb_synopsis(soup)

    genres = []
    genre_div = soup.find("div", class_="genxed")
    if genre_div:
        genres = [a.text.strip() for a in genre_div.find_all("a") if a.text.strip()]

    details = {}
    info_div = soup.find("div", class_="spe")
    if info_div:
        for span in info_div.find_all("span"):
            key, sep, value = span.text.partition(":")
            if sep and key.strip() not in details:
                details[key.strip()] = value.strip()

    download_links = []
    dl_box = soup.find("div", class_="dlbox")
    if dl_box:
        for li in dl_box.find_all("li")[1:]:
            server_elem = li.find("span", class_="q")
            quality_elem = li.find("span", class_="w")
            link_elem = li.find("span", class_="e")
            link_anchor = link_elem.find("a", href=True) if link_elem else None
            if not link_anchor:
                continue
            download_links.append(
                {
                    "server": server_elem.text.strip() if server_elem else "Unknown Server",
                    "kualitas": quality_elem.text.strip() if quality_elem else "Unknown Quality",
                    "url": link_anchor["href"],
                }
            )

    return {
        "title": title_elem.text.strip() if title_elem else "Judul tidak ditemukan",
        "rating": rating_elem.strong.text.strip() if rating_elem and rating_elem.strong else "Rating tidak ada",
        "synopsis": synopsis,
        "genres": genres,
        "details": details,
        "download_links": download_links,
    }


def format_oppaweb_detail(data: dict):
    genres = ", ".join(escape(i) for i in data["genres"]) or "-"
    result = (
        f"<b>Judul:</b> {escape(data['title'])}\n"
        f"<b>Rating:</b> {escape(data['rating'])}\n"
        f"<b>Genre:</b> {genres}\n\n"
        f"<b>Sinopsis:</b>\n{escape(data['synopsis'])}\n"
    )
    if data["details"]:
        result += "\n<b>--- Detail Info ---</b>\n"
        for key, value in data["details"].items():
            result += f"<b>{escape(key)}:</b> {escape(value)}\n"
    result += "\n<b>--- Link Download ---</b>\n"
    if data["download_links"]:
        for dl in data["download_links"]:
            url = escape(dl["url"], quote=True)
            result += (
                f"[{escape(dl['kualitas'])}] {escape(dl['server'])} "
                f"-&gt; <a href='{url}'>{url}</a>\n"
            )
    else:
        result += "Link download tidak ditemukan."
    return result


# Terbit21 GetData
async def getDataTerbit21(msg, kueri, CurrentPage, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                if kueri:
                    terbitjson = await fetch.get(
                        f"{web['yasirapi']}/terbit21?q={kueri}"
                    )
                else:
                    terbitjson = await fetch.get(f"{web['yasirapi']}/terbit21")
                terbitjson.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>"
                )
                return None, None
        res = terbitjson.json()
        if not res.get("result"):
            await msg.edit(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(msg.id, [split_arr(res["result"], 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    if kueri:
        TerbitRes = strings("header_with_query").format(web="Terbit21", kueri=kueri)
    else:
        TerbitRes = strings("header_no_query").format(web="Terbit21", cmd="terbit21")
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        TerbitRes += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('cat_text')}:</b> <code>{i['kategori']}</code>\n"
        TerbitRes += (
            "\n"
            if re.search(r"Complete|Ongoing", i["kategori"])
            else f"<b><a href='{i['dl']}'>{strings('dl_text')}</a></b>\n\n"
        )
    return TerbitRes, PageLen


async def _scrape_lk21_direct(kueri, page: int = 1) -> list[dict]:
    """Scrape LK21 langsung dari situs (fallback saat API yasirapi kosong).

    Cloudflare memblokir User-Agent curl biasa, jadi pakai Googlebot UA.
    """
    base = web.get("lk21") or DEFAULT_WEB["lk21"]
    if not base.startswith(("http://", "https://")):
        base = f"https://{base}"
    headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    if kueri:
        url = f"{base}/?s={quote_plus(kueri)}"
    else:
        url = f"{base}/latest"
        if page > 1:
            url += f"/page/{page}"
    resp = await resp_get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()
    # Setelah redirect (misal tv10 -> tv12), pakai URL final sebagai base
    final_base = str(resp.url).rstrip("/")
    html = resp.text
    articles = re.findall(r"<article.*?</article>", html, re.DOTALL)
    result = []
    for b in articles:
        href = re.search(r'<a href="([^"]+)"[^>]*itemprop="url"', b)
        title = re.search(r'<h3 class="poster-title"[^>]*>([^<]+)</h3>', b)
        genre = re.search(r'<div class="genre">\s*([^<]+?)\s*</div>', b)
        if not href or not title:
            continue
        link = href.group(1)
        if link.startswith("/"):
            link = urljoin(final_base, link)
        result.append(
            {
                "link": link,
                "judul": title.group(1).strip(),
                "kategori": genre.group(1).strip() if genre else "Movie",
                "dl": link,
            }
        )
    return result


# LK21 GetData
async def getDatalk21(msg, kueri, CurrentPage, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        result = []
        try:
            with contextlib.redirect_stdout(sys.stderr):
                if kueri:
                    lk21json = await fetch.get(f"{web['yasirapi']}/lk21?q={kueri}")
                else:
                    lk21json = await fetch.get(f"{web['yasirapi']}/lk21")
                lk21json.raise_for_status()
                result = lk21json.json().get("result") or []
        except (httpx.HTTPError, ValueError) as exc:
            # API error / response bukan JSON -> fallback scrape langsung
            LOGGER.warning("LK21 API gagal (%s), fallback ke scrape langsung", exc)
        if not result:
            try:
                result = await _scrape_lk21_direct(kueri)
            except Exception as exc:
                LOGGER.exception("LK21 direct scrape gagal")
                await msg.edit(
                    f"ERROR: Gagal mengambil data LK21 - <code>{exc}</code>"
                )
                return None, None
        if not result:
            await msg.edit(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(msg.id, [split_arr(result, 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    if kueri:
        lkResult = strings("header_with_query").format(web="Layarkaca21", kueri=kueri)
    else:
        lkResult = strings("header_no_query").format(web="Layarkaca21", cmd="lk21")
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        lkResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('cat_text')}:</b> <code>{i['kategori']}</code>\n"
        lkResult += (
            "\n"
            if re.search(r"Complete|Ongoing", i["kategori"])
            else f"<b><a href='{i['dl']}'>{strings('dl_text')}</a></b>\n\n"
        )
    return lkResult, PageLen


# Pahe GetData
async def getDataPahe(msg, kueri, CurrentPage, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                if kueri:
                    pahejson = await fetch.get(
                        f"{web['yasirapi']}/pahe?q={kueri}&domain={web['pahe']}"
                    )
                else:
                    pahejson = await fetch.get(
                        f"{web['yasirapi']}/pahe?domain={web['pahe']}"
                    )
                pahejson.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>"
                )
                return None, None
        res = pahejson.json()
        if not res.get("result"):
            await msg.edit(strings("no_result"), del_in=5)
            return None, None
        SCRAP_DICT.add(msg.id, [split_arr(res["result"], 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    paheResult = (
        strings("header_with_query").format(web="Pahe", kueri=kueri)
        if kueri
        else strings("header_no_query").format(web="Pahe", cmd="pahe")
    )
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        paheResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n\n"
    return paheResult, PageLen


# Kusonime GetData
async def getDataKuso(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        kusodata = []
        with contextlib.redirect_stdout(sys.stderr):
            try:
                data = await fetch.get(
                    f"{web['kusonime']}/?s={kueri}", follow_redirects=True
                )
                data.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None, None
        res = BeautifulSoup(data, "lxml").find_all("h2", {"class": "episodeye"})
        for i in res:
            ress = i.find_all("a")[0]
            title = ress.text
            link = ress["href"]
            kusodata.append({"title": title, "link": link})
        if not kusodata:
            await msg.edit(strings("no_result"), del_in=5)
            return None, 0, None, None
        SCRAP_DICT.add(msg.id, [split_arr(kusodata, 10), kueri], timeout=1800)
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
    return kusoResult, PageLen, extractbtn1, extractbtn2


# Movieku GetData
async def getDataMovieku(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        moviekudata = []
        with contextlib.redirect_stdout(sys.stderr):
            try:
                data = await fetch.get(
                    f"{web['movieku']}/?s={kueri}", follow_redirects=True
                )
                data.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>"
                )
                return None, 0, None
        r = BeautifulSoup(data, "lxml")
        res = r.find_all(class_="bx")
        for i in res:
            judul = i.find_all("a")[0]["title"]
            link = i.find_all("a")[0]["href"]
            typ = i.find(class_="overlay").text
            typee = typ.strip() if typ.strip() != "" else "~"
            moviekudata.append({"judul": judul, "link": link, "type": typee})
        if not moviekudata:
            await msg.edit(strings("no_result"), del_in=5)
            return None, 0, None
        SCRAP_DICT.add(msg.id, [split_arr(moviekudata, 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    extractbtn = []

    moviekuResult = (
        strings("header_no_query").format(web="Movieku", cmd="movieku")
        if kueri == ""
        else strings("header_with_query").format(web="Movieku", kueri=kueri)
    )
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        moviekuResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>{strings('quality')}/Status:</b> {i['type']}\n\n"
        extractbtn.append(
            InlineButton(
                index * 6 + c, f"moviekuextract#{CurrentPage}#{c}#{user}#{msg.id}"
            )
        )
    return moviekuResult, PageLen, extractbtn


# NoDrakor GetData
async def getDataNodrakor(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        nodrakordata = []
        with contextlib.redirect_stdout(sys.stderr):
            try:
                data = await fetch.get(
                    f"{web['nodrakor']}/?s={kueri}",
                    follow_redirects=True,
                )
                data.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        text = BeautifulSoup(data, "lxml")
        entry = text.find_all(class_="entry-header")
        if not entry or entry[0].text.strip() in ("Nothing Found", "Tidak Ditemukan"):
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        for i in entry:
            genre = i.find(class_="gmr-movie-on")
            genre = f"{genre.text}" if genre else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            nodrakordata.append({"judul": judul, "link": link, "genre": genre})
        SCRAP_DICT.add(msg.id, [split_arr(nodrakordata, 6), kueri], timeout=1800)
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
    return nodrakorResult, PageLen, extractbtn


# Savefilm21 GetData
async def getDataSavefilm21(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        sfdata = []
        with contextlib.redirect_stdout(sys.stderr):
            try:
                data = await fetch.get(
                    f"{web['savefilm21']}/?s={kueri}",
                    follow_redirects=True,
                )
                data.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        text = BeautifulSoup(data, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Tidak Ditemukan" in entry[0].text:
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(
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
    return sfResult, PageLen, extractbtn


# NunaDrama GetData
async def getDataNunaDrama(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                nunafetch = await fetch.get(
                    f"{web['nunadrama']}/?s={kueri}", follow_redirects=True
                )
                nunafetch.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        text = BeautifulSoup(nunafetch, "lxml")
        entry = text.find_all(class_="entry-header")
        if not entry or entry[0].text.strip() in ("Nothing Found", "Tidak Ditemukan"):
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        else:
            data = []
            for i in entry:
                genre = i.find(class_="gmr-movie-on")
                genre = f"{genre.text}" if genre else "N/A"
                judul = i.find(class_="entry-title").find("a").text
                link = i.find(class_="entry-title").find("a").get("href")
                data.append({"judul": judul, "link": link, "genre": genre})
            SCRAP_DICT.add(msg.id, [split_arr(data, 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    extractbtn = []

    nunaResult = (
        strings("header_with_query").format(web="NunaDrama", kueri=kueri)
        if kueri
        else strings("header_no_query").format(web="NunaDrama", cmd="nunadrama")
    )
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        nunaResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n\n"
        if not re.search(r"Series", i["genre"]):
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"nunaextract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
    nunaResult += strings("unsupport_dl_btn")
    return nunaResult, PageLen, extractbtn


# PusatFilm21 GetData
async def getDataPusatFilm(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                nunafetch = await fetch.get(
                    f"{web['pusatfilm']}/?s={kueri}", follow_redirects=True
                )
                nunafetch.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        text = BeautifulSoup(nunafetch, "lxml")
        entry = text.find_all(class_="entry-header")
        if not entry or entry[0].text.strip() in ("Nothing Found", "Tidak Ditemukan"):
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        else:
            data = []
            for i in entry:
                genre = i.find(class_="gmr-movie-on")
                genre = f"{genre.text}" if genre else "N/A"
                judul = i.find(class_="entry-title").find("a").text
                link = i.find(class_="entry-title").find("a").get("href")
                data.append({"judul": judul, "link": link, "genre": genre})
            SCRAP_DICT.add(msg.id, [split_arr(data, 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    extractbtn = []

    pfResult = (
        strings("header_with_query").format(web="PusatFilm21", kueri=kueri)
        if kueri
        else strings("header_no_query").format(web="PusatFilm21", cmd="pusatfilm")
    )
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        pfResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n\n"
        if not re.search(r"Series", i["genre"]):
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"pfextract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
    pfResult += strings("unsupport_dl_btn")
    return pfResult, PageLen, extractbtn


# DutaMovie GetData
async def getDataDutaMovie(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                nunafetch = await fetch.get(
                    f"{web['dutamovie']}/?s={kueri}", follow_redirects=True
                )
                nunafetch.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        text = BeautifulSoup(nunafetch, "lxml")
        entry = text.find_all(class_="entry-header")
        if not entry or entry[0].text.strip() in ("Nothing Found", "Tidak Ditemukan"):
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        else:
            data = []
            for i in entry:
                genre = i.find(class_="gmr-movie-on")
                genre = f"{genre.text}" if genre else "N/A"
                judul = i.find(class_="entry-title").find("a").text
                link = i.find(class_="entry-title").find("a").get("href")
                data.append({"judul": judul, "link": link, "genre": genre})
            SCRAP_DICT.add(msg.id, [split_arr(data, 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    extractbtn = []

    dutaResult = (
        strings("header_with_query").format(web="DutaMovie", kueri=kueri)
        if kueri
        else strings("header_no_query").format(web="DutaMovie", cmd="dutamovie")
    )
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        dutaResult += f"<b>{index*6+c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n\n"
        if not re.search(r"Series", i["genre"]):
            extractbtn.append(
                InlineButton(
                    index * 6 + c, f"dutaextract#{CurrentPage}#{c}#{user}#{msg.id}"
                )
            )
    dutaResult += strings("unsupport_dl_btn")
    return dutaResult, PageLen, extractbtn


# OppaWeb GetData
async def getDataOppaweb(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        oppawebdata = []
        with contextlib.redirect_stdout(sys.stderr):
            try:
                for page in range(1, OPPAWEB_MAX_PAGES + 1):
                    data = await fetch.get(
                        oppaweb_search_url(kueri, page),
                        headers=oppaweb_request_headers(),
                        cookies=OPPAWEB_COOKIES,
                        follow_redirects=True,
                    )
                    data.raise_for_status()
                    page_results, has_next = parse_oppaweb_search(data.text)
                    oppawebdata.extend(page_results)
                    if not has_next:
                        break
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        if not oppawebdata:
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(strings("no_result_w_query").format(kueri=kueri), del_in=5)
            return None, 0, None
        SCRAP_DICT.add(msg.id, [split_arr(oppawebdata, 6), kueri], timeout=1800)
    index = int(CurrentPage - 1)
    PageLen = len(SCRAP_DICT[msg.id][0])
    extractbtn = []

    oppawebResult = (
        strings("header_no_query").format(web="OppaWeb", cmd="oppaweb")
        if kueri == ""
        else strings("header_with_query").format(web="OppaWeb", kueri=kueri)
    )
    for c, i in enumerate(SCRAP_DICT[msg.id][0][index], start=1):
        oppawebResult += (
            f"<b>{index*6+c}. <a href='{escape(i['link'], quote=True)}'>{escape(i['judul'])}</a></b>\n"
            f"<b>Tipe:</b> <code>{escape(i['type'])}</code>\n"
            f"<b>Status:</b> <code>{escape(i['status'])}</code> [<code>{escape(i['subtitle'])}</code>]\n\n"
        )
        extractbtn.append(
            InlineButton(
                index * 6 + c, f"oppawebextract#{CurrentPage}#{c}#{user}#{msg.id}"
            )
        )
    return oppawebResult, PageLen, extractbtn


# Lendrive GetData
async def getDataLendrive(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                if kueri:
                    data = await fetch.get(
                        f"{web['lendrive']}/?s={kueri}",
                        follow_redirects=True,
                    )
                else:
                    data = await fetch.get(web["lendrive"], follow_redirects=True)
                data.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
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
                {
                    "judul": title,
                    "link": link,
                    "quality": kualitas or "N/A",
                    "status": status,
                }
            )
        if not lenddata:
            await msg.edit(strings("no_result"), del_in=5)
            return None, 0, None
        savedict[msg.id] = [split_arr(lenddata, 6), kueri]
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
    return lenddataResult, PageLen, extractbtn


# MelongMovie GetData
async def getDataMelong(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                data = await fetch.get(
                    f"{web['melongmovie']}/?s={kueri}",
                    follow_redirects=True,
                )
                data.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        bs4 = BeautifulSoup(data, "lxml")
        melongdata = []
        for res in bs4.select(".box"):
            dd = res.select("a")
            url = dd[0]["href"]
            title = dd[0]["title"]
            try:
                quality = dd[0].find(class_="quality").text
            except Exception:
                quality = "N/A"
            melongdata.append({"judul": title, "link": url, "quality": quality})
        if not melongdata:
            await msg.edit(strings("no_result"), del_in=5)
            return None, 0, None
        SCRAP_DICT.add(msg.id, [split_arr(melongdata, 6), kueri], timeout=1800)
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
    return melongResult, PageLen, extractbtn


# GoMov GetData
async def getDataGomov(msg, kueri, CurrentPage, user, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        with contextlib.redirect_stdout(sys.stderr):
            try:
                gomovv = await fetch.get(
                    f"{web['gomov']}/?s={kueri}", follow_redirects=True
                )
                gomovv.raise_for_status()
            except httpx.HTTPError as exc:
                await msg.edit(
                    f"ERROR: Failed to fetch data from {exc.request.url} - <code>{exc}</code>",
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                )
                return None, 0, None
        text = BeautifulSoup(gomovv, "lxml")
        entry = text.find_all(class_="entry-header")
        if not entry or entry[0].text.strip() in ("Nothing Found", "Tidak Ditemukan"):
            if not kueri:
                await msg.edit(strings("no_result"), del_in=5)
            else:
                await msg.edit(
                    strings("no_result_w_query").format(kueri=kueri), del_in=5
                )
            return None, 0, None
        else:
            data = []
            for i in entry:
                genre = i.find(class_="gmr-movie-on")
                genre = f"{genre.text}" if genre else "N/A"
                judul = i.find(class_="entry-title").find("a").text
                link = i.find(class_="entry-title").find("a").get("href")
                data.append({"judul": judul, "link": link, "genre": genre})
            SCRAP_DICT.add(msg.id, [split_arr(data, 6), kueri], timeout=1800)
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
    return gomovResult, PageLen, extractbtn


# getData samehada
async def getSame(msg, query, current_page, strings):
    await ensure_web_config()
    if not SCRAP_DICT.get(msg.id):
        cfse = cloudscraper.create_scraper()
        if query:
            data = cfse.get(f"{web['samehadaku']}/?s={query}")
        else:
            data = cfse.get(web["samehadaku"])
        if data.status_code != 200:
            await msg.edit(strings("err_getweb").format(err=data.status_code))
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
            await msg.edit(strings("no_result"), del_in=5)
            return None, None
        savedict[msg.id] = [split_arr(sdata, 10), query]
    index = int(current_page - 1)
    PageLen = len(savedict[msg.id][0])
    sameresult = "".join(
        f"<b>{index * 6 + c}. <a href='{i['url']}'>{i['title']}</a>\n<b>Status:</b> {i['sta']}\n</b>Rating:</b> {i['rate']}\n\n"
        for c, i in enumerate(savedict[msg.id][0][index], start=1)
    )
    return sameresult, PageLen


# ============================================================
# GENERIC SCRAPER HANDLERS (command + page callback)
# Mapping: command -> (getdata_fn, page_prefix, needs_user)
# ============================================================
SCRAPER_REGISTRY = {
    "samehadaku": (getSame, "page_same", False),
    "terbit21": (getDataTerbit21, "page_terbit21", False),
    "lk21": (getDatalk21, "page_lk21", False),
    "pahe": (getDataPahe, "page_pahe", False),
    "gomov": (getDataGomov, "page_gomov", True),
    "klikxxi": (getDataGomov, "page_gomov", True),
    "melongmovie": (getDataMelong, "page_melong", True),
    "nunadrama": (getDataNunaDrama, "page_nuna", True),
    "pusatfilm": (getDataPusatFilm, "page_pf", True),
    "dutamovie": (getDataDutaMovie, "page_duta", True),
    "savefilm21": (getDataSavefilm21, "page_sf21", True),
    "nodrakor": (getDataNodrakor, "page_nodrakor", True),
    "kusonime": (getDataKuso, "page_kuso", True),
    "lendrive": (getDataLendrive, "page_lendrive", True),
    "movieku": (getDataMovieku, "page_movieku", True),
    "oppaweb": (getDataOppaweb, "page_oppaweb", True),
}

PAGE_REGISTRY = {v[1]: (v[0], v[2]) for v in SCRAPER_REGISTRY.values()}


@app.on_cmd(list(SCRAPER_REGISTRY.keys()), no_channel=True)
@use_chat_lang()
async def scraper_cmd(_, message, strings):
    cmd = message.command[0].lower().lstrip("/")
    func, page_prefix, needs_user = SCRAPER_REGISTRY[cmd]
    kueri = " ".join(message.command[1:]) or None
    pesan = await message.reply(strings("get_data"))
    if needs_user:
        unpacked = await func(pesan, kueri, 1, message.from_user.id, strings)
        if len(unpacked) == 4:
            # getDataKuso punya 2 baris tombol (extractbtn1 + extractbtn2)
            res, PageLen, btn1, btn2 = unpacked
            btn = btn1 + btn2
        else:
            res, PageLen, btn = unpacked
    else:
        res, PageLen = await func(pesan, kueri, 1, strings)
    if not res:
        return
    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        1,
        f"{page_prefix}#{{number}}" + f"#{pesan.id}#{message.from_user.id}",
    )
    if needs_user:
        keyboard.row(InlineButton(strings("ex_data"), user_id=_.me.id))
        keyboard.row(*btn)
    keyboard.row(InlineButton(strings("cl_btn"), f"close#{message.from_user.id}"))
    await pesan.edit(
        res,
        link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        reply_markup=keyboard,
    )


@app.on_cb("page_")
@use_chat_lang()
async def scraper_page_callback(_, callback_query, strings):
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            return await callback_query.answer(strings("unauth"), True)
        message_id = int(callback_query.data.split("#")[2])
        CurrentPage = int(callback_query.data.split("#")[1])
        kueri = SCRAP_DICT[message_id][1]
    except (IndexError, ValueError):
        return
    except KeyError:
        return await callback_query.message.edit(strings("invalid_cb"))
    except QueryIdInvalid:
        return

    prefix = callback_query.data.split("#")[0]
    func, needs_user = PAGE_REGISTRY.get(prefix, (None, False))
    if not func:
        return
    try:
        if needs_user:
            unpacked = await func(
                callback_query.message, kueri, CurrentPage, callback_query.from_user.id, strings
            )
            if len(unpacked) == 4:
                # getDataKuso punya 2 baris tombol (extractbtn1 + extractbtn2)
                res, PageLen, btn1, btn2 = unpacked
                btn = btn1 + btn2
            else:
                res, PageLen, btn = unpacked
        else:
            res, PageLen = await func(callback_query.message, kueri, CurrentPage, strings)
    except TypeError:
        return

    keyboard = InlineKeyboard()
    keyboard.paginate(
        PageLen,
        CurrentPage,
        f"{prefix}#{{number}}" + f"#{message_id}#{callback_query.from_user.id}",
    )
    if needs_user:
        keyboard.row(InlineButton(strings("ex_data"), user_id=_.me.id))
        keyboard.row(*btn)
    keyboard.row(
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}")
    )
    await callback_query.message.edit(
        res,
        link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
        reply_markup=keyboard,
    )


# ============================================================
# GENERIC EXTRACT HANDLER (semua *extract# callback)
# Dispatch ke fungsi per-situs; parsing + keyboard terpusat
# ============================================================
async def _extract_cb_parse(callback_query, strings, back_prefix, store):
    """Parse callback data + buat keyboard back/close. Return (link, keyboard) atau None."""
    try:
        if callback_query.from_user.id != int(callback_query.data.split("#")[3]):
            await callback_query.answer(strings("unauth"), True)
            return None
        idlink = int(callback_query.data.split("#")[2])
        message_id = int(callback_query.data.split("#")[4])
        CurrentPage = int(callback_query.data.split("#")[1])
        link = store[message_id][0][CurrentPage - 1][idlink - 1].get("link")
    except (IndexError, ValueError):
        return None
    except KeyError:
        await callback_query.message.edit(strings("invalid_cb"))
        return None
    except QueryIdInvalid:
        return None

    keyboard = InlineKeyboard()
    keyboard.row(
        InlineButton(
            strings("back_btn"),
            f"{back_prefix}#{CurrentPage}#{message_id}#{callback_query.from_user.id}",
        ),
        InlineButton(strings("cl_btn"), f"close#{callback_query.from_user.id}"),
    )
    return link, keyboard


@app.on_cb(r"^(oppaweb|kuso|sf21|nuna|pf|duta|nodrakor|movieku|melong|gomov|lendrive)extract#")
@use_chat_lang()
async def scraper_extract_cb(client, callback_query, strings):
    prefix = callback_query.data.split("#")[0]
    entry = EXTRACT_REGISTRY.get(prefix)
    if not entry:
        return
    back_prefix, handler = entry
    store = savedict if prefix == "lendriveextract" else SCRAP_DICT
    parsed = await _extract_cb_parse(callback_query, strings, back_prefix, store)
    if not parsed:
        return
    link, keyboard = parsed
    await handler(client, callback_query, strings, link, keyboard)


# ============================================================
# LOGIKA EXTRACT PER SITUS (bukan handler, dipanggil via registry)
# ============================================================
async def _extract_oppaweb(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(
                link,
                headers=oppaweb_request_headers(link),
                cookies=OPPAWEB_COOKIES,
                follow_redirects=True,
            )
            html.raise_for_status()
            source_data = parse_oppaweb_detail(html.text)
            detail_url = parse_oppaweb_episode_link(html.text) or link
            detail_data = source_data
            if detail_url != link:
                html = await fetch.get(
                    detail_url,
                    headers=oppaweb_request_headers(link),
                    cookies=OPPAWEB_COOKIES,
                    follow_redirects=True,
                )
                html.raise_for_status()
                detail_data = parse_oppaweb_detail(html.text)
                if detail_data["synopsis"] == "Sinopsis tidak ditemukan":
                    detail_data["synopsis"] = source_data["synopsis"]
                if not detail_data["genres"]:
                    detail_data["genres"] = source_data["genres"]
                if not detail_data["details"]:
                    detail_data["details"] = source_data["details"]
            res = format_oppaweb_detail(detail_data)
            await callback_query.message.edit(
                strings("res_scrape").format(link=detail_url, kl=res),
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
                reply_markup=keyboard,
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(f"ERROR: {err}", reply_markup=keyboard)


async def _extract_kuso(client, callback_query, strings, link, keyboard):
    kuso = Kusonime()
    try:
        if init_url := data_kuso.get(link, False):
            await callback_query.message.edit(
                init_url.get("ph_url"), reply_markup=keyboard
            )
        tgh = await kuso.telegraph(link, client.me.username)
        data_kuso[link] = {"ph_url": tgh}
        return await callback_query.message.edit(tgh, reply_markup=keyboard)
    except Exception as e:
        LOGGER.error(f"clases: {e.__class__}, moduleName: {e.__class__.__name__}")
        if str(e).startswith("ERROR"):
            return await callback_query.message.edit(e, reply_markup=keyboard)


async def _extract_savefilm21(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            res = soup.find_all(class_="button button-shadow")
            res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_nuna(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            # Struktur baru: <div class="gmr-download-wrap"> berisi tombol download
            download_section = soup.find("div", class_="gmr-download-wrap")
            if not download_section:
                # fallback selector lama
                download_section = soup.find("div", class_="dzdesu")
            if not download_section:
                await callback_query.message.edit(
                    f"ERROR: No download section found on {link}", reply_markup=keyboard
                )
                return
            title_el = download_section.find("h3") or download_section.find("h2")
            title = title_el.text.strip() if title_el else "N/A"
            links = download_section.find_all("a", href=True)
            download_links = {link.text.strip(): link["href"] for link in links}
            res = f"<b>Judul</b>: {title}\n\n<b>Link Download:</b>\n"
            for label, dl_link in download_links.items():
                res += f"{label}: <a href='{dl_link}'>{dl_link}</a>\n"
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_pusatfilm(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            ddl = soup.find("li", {"pull-right"}).find("a").get("href")
            res = f"<b>Link Download:</b> {ddl}"
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_duta(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            download_section = soup.find("div", id="gmr-id-download")
            title = download_section.find("h3", class_="title-download").text.strip()
            links = download_section.find_all("a", href=True)
            download_links = {link['title']: link['href'] for link in links}
            res = f"<b>Judul</b>: {title}\n\n<b>Link Download:</b>\n"
            for label, link in download_links.items():
                res += f"{label}: {link}\n\n"
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_nodrakor(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            if "/tv/" in link:
                result = soup.find(
                    "div", {"entry-content entry-content-single"}
                ).find_all("p")
                msg = "".join(str(f"{i}\n") for i in result)
                link = await post_to_telegraph(False, "MissKaty NoDrakor", msg)
                return await callback_query.message.edit(
                    strings("res_scrape").format(link=link, kl=link),
                    reply_markup=keyboard,
                )
            res = soup.find_all(class_="button button-shadow")
            res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
            if len(res) > 3500:
                link = await post_to_telegraph(False, "MissKaty NoDrakor", res)
                return await callback_query.message.edit(
                    strings("res_scrape").format(link=link, kl=link),
                    reply_markup=keyboard,
                )
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=res), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_movieku(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            data = {}
            output = []
            total_links = 0
            valid_resolutions = {'1080p', '720p', '480p', '360p'}
            current_title = None

            for element in soup.find_all(['h3', 'p']):
                if element.name == 'h3' and 'smokettl' in element.get('class', []):
                    current_title = element.text.strip()
                    if current_title not in data:
                        data[current_title] = []
                elif element.name == 'p' and current_title:
                    strong_tag = element.find('strong')
                    if strong_tag:
                        resolution = strong_tag.text.strip()
                        if resolution in valid_resolutions:
                            total_links += 1
                            links = ', '.join([f'<a href="{a["href"]}">{a.text.strip()}</a>' for a in element.find_all('a')])
                            data[current_title].append(f"{resolution} {links}")

            for title, resolutions in data.items():
                output.append(title)
                output.extend(resolutions)
                output.append('')
            if total_links > 70:
                url = await post_to_telegraph(False, link, "<br>".join(output))
                return await callback_query.message.edit(strings("res_scrape").format(link=link, kl=f"Your result is too long, i have pasted your result on Telegraph:\n{url}"), reply_markup=keyboard)
            if "\n".join(output) == "":
                output = "\nOpen link in browser, click on episode page and use /movieku_scrap [page link] commands for extract download link"
                return await callback_query.message.edit(strings("res_scrape").format(link=link, kl=output), reply_markup=keyboard)
            await callback_query.message.edit(strings("res_scrape").format(link=link, kl="\n".join(output)), reply_markup=keyboard)
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_melong(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            rep = ""
            for ep in soup.findAll(text=re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
                hardsub = ep.findPrevious("div")
                softsub = ep.findNext("div")
                rep += f"{hardsub}\n{softsub}"
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=rep), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_gomov(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
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
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=hasil), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


async def _extract_lendrive(client, callback_query, strings, link, keyboard):
    with contextlib.redirect_stdout(sys.stderr):
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
                    f"[ <a href='{a.get('href')}'>{a.text}</a> ]\n"
                    for a in i.findAll("a")
                )
            await callback_query.message.edit(
                strings("res_scrape").format(link=link, kl=kl), reply_markup=keyboard
            )
        except httpx.HTTPError as exc:
            await callback_query.message.edit(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>",
                reply_markup=keyboard,
            )
        except Exception as err:
            await callback_query.message.edit(
                f"ERROR: {err}", reply_markup=keyboard
            )


EXTRACT_REGISTRY = {
    "oppawebextract": ("page_oppaweb", _extract_oppaweb),
    "kusoextract": ("page_kuso", _extract_kuso),
    "sf21extract": ("page_sf21", _extract_savefilm21),
    "nunaextract": ("page_nuna", _extract_nuna),
    "pfextract": ("page_pf", _extract_pusatfilm),
    "dutaextract": ("page_duta", _extract_duta),
    "nodrakorextract": ("page_nodrakor", _extract_nodrakor),
    "moviekuextract": ("page_movieku", _extract_movieku),
    "melongextract": ("page_melong", _extract_melong),
    "gomovextract": ("page_gomov", _extract_gomov),
    "lendriveextract": ("page_lendrive", _extract_lendrive),
}


# Manual Scrape DDL Movieku.CC incase cannot auto scrape from button
@app.on_cmd("movieku_scrap")
@use_chat_lang()
async def muviku_scrap(_, message, strings):
    with contextlib.redirect_stdout(sys.stderr):
        try:
            link = message.text.split(maxsplit=1)[1]
            html = await fetch.get(link)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, "lxml")
            data = {}
            output = []
            total_links = 0
            valid_resolutions = {'1080p', '720p', '480p', '360p'}
            current_title = None

            for element in soup.find_all(['h3', 'p']):
                if element.name == 'h3' and 'smokettl' in element.get('class', []):
                    current_title = element.text.strip()
                    if current_title not in data:
                        data[current_title] = []
                elif element.name == 'p' and current_title:
                    strong_tag = element.find('strong')
                    if strong_tag:
                        resolution = strong_tag.text.strip()
                        if resolution in valid_resolutions:
                            links = ', '.join([f'<a href="{a["href"]}">{a.text.strip()}</a>' for a in element.find_all('a')])
                            data[current_title].append(f"{resolution} {links}")

            for title, resolutions in data.items():
                output.append(title)
                output.extend(resolutions)
                output.append('')
                for res in resolutions:
                    total_links += res.count('<a href=')
            if not data:
                return await message.reply(strings("no_result"))
            if total_links > 70:
                url = await post_to_telegraph(False, link, "<br>".join(output))
                return await message.reply(f"Your result is too long, i have pasted your result on Telegraph:\n{url}")
            await message.reply("\n".join(output))
        except IndexError:
            return await message.reply(
                strings("invalid_cmd_scrape").format(cmd=message.command[0])
            )
        except httpx.HTTPError as exc:
            await message.reply(
                f"HTTP Exception for {exc.request.url} - <code>{exc}</code>"
            )
        except Exception as e:
            await message.reply(f"ERROR: {str(e)}")




