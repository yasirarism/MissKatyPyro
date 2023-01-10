"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""

import asyncio
import re
from logging import getLogger

from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "WebScraper"
__HELP__ = """
/melongmovie - Scrape website data from MelongMovie Web. If without query will give latest movie list.
/lk21 [query <optional>] - Scrape website data from LayarKaca21. If without query will give latest movie list.
/pahe [query <optional>] - Scrape website data from Pahe.li. If without query will give latest post list.
/terbit21 [query <optional>] - Scrape website data from Terbit21. If without query will give latest movie list.
/savefilm21 [query <optional>] - Scrape website data from Savefilm21. If without query will give latest movie list.
/movieku [query <optional>] - Scrape website data from Movieku.cc
/nodrakor [query] - Scrape website data from nodrakor.icu
/zonafilm [query] - Scrape website data from zonafilm.icu
/gomov [query <optional>] - Scrape website data from GoMov. If without query will give latest movie list.
"""

LOGGER = getLogger(__name__)

headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}


@app.on_message(filters.command(["zonafilm"], COMMAND_HANDLER))
@capture_err
async def zonafilm(_, msg):
    m = await msg.reply("**__⏳ Please wait, scraping data ...__**", True)
    try:
        title = msg.text.split(" ", 1)[1]
    except IndexError:
        title = ""
    try:
        html = await http.get(f"https://zonafilm.icu/?s={title}", headers=headers)
        text = BeautifulSoup(html.text, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Nothing Found" in entry[0].text:
            await m.delete()
            if title != "":
                await msg.reply(f"404 Not FOUND For: {title}", True)
            else:
                await msg.reply(f"404 Not FOUND!", True)
            return
        data = []
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            data.append({"judul": judul, "link": link, "genre": genre})
        if title != "":
            head = f"<b>#Zonafilm Results For:</b> <code>{title}</code>\n\n"
        else:
            head = f"<b>#Zonafilm Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
        msgs = ""
        await m.delete()
        for c, i in enumerate(data, start=1):
            msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n"
            msgs += f"<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n" if not "/tv/" in i["link"] else "\n"
            if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
                await asyncio.sleep(2)
                msgs = ""
        if msgs != "":
            await msg.reply(
                head + msgs,
                True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="❌ Close",
                                callback_data=f"close#{msg.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
    except Exception as e:
        LOGGER.error(e)
        await m.delete()
        await msg.reply(f"ERROR: <code>{e}</code>", True)


@app.on_message(filters.command(["nodrakor"], COMMAND_HANDLER))
@capture_err
async def nodrakor(_, msg):
    m = await msg.reply("**__⏳ Please wait, scraping data ...__**", True)
    try:
        title = msg.text.split(" ", 1)[1]
    except IndexError:
        title = ""
    try:
        html = await http.get(f"http://173.212.199.27/?s={title}", headers=headers)
        text = BeautifulSoup(html.text, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Nothing Found" in entry[0].text:
            await m.delete()
            if title != "":
                await msg.reply(f"404 Not FOUND For: {title}", True)
            else:
                await msg.reply(f"404 Not FOUND!", True)
            return
        data = []
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre[:-2]}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            data.append({"judul": judul, "link": link, "genre": genre})
        if title != "":
            head = f"<b>#Nodrakor Results For:</b> <code>{title}</code>\n\n"
        else:
            head = f"<b>#Nodrakor Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
        msgs = ""
        await m.delete()
        for c, i in enumerate(data, start=1):
            msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
            if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
                await asyncio.sleep(2)
                msgs = ""
        if msgs != "":
            await msg.reply(head + msgs, True, disable_web_page_preview=True)
    except Exception as e:
        LOGGER.error(e)
        await m.delete()
        await msg.reply(f"ERROR: <code>{e}</code>", True)


# Broken
@app.on_message(filters.command(["ngefilm21"], COMMAND_HANDLER))
@capture_err
async def ngefilm21(_, message):
    if len(message.command) == 1:
        return await message.reply("Masukkan query yang akan dicari..!!")
    title = message.text.split(" ", maxsplit=1)[1]

    msg = await message.reply("Sedang proses scrap, mohon tunggu..")
    try:
        html = await http.get(f"https://ngefilm.info/search?q={title}", headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all("h2")
        data = []
        for i in res:
            a = i.find_all("a")[0]
            judul = a.find_all(class_="r-snippetized")
            b = i.find_all("a")[0]["href"]
            data.append({"judul": judul[0].text, "link": b})
            # print(f"{judul[0].text}{b}\n")
        if not data:
            return await msg.edit("Oops, data film tidak ditemukan.")
        res = "".join(f"<b>{i['judul']}</b>\n{i['link']}\n" for i in data)
        await msg.edit(
            f"<b>Hasil Scrap dari Ngefilm21:</b>\n{res}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❌ Close",
                            callback_data=f"close#{message.from_user.id}",
                        )
                    ]
                ]
            ),
        )
    except Exception as e:
        await msg.edit(f"ERROR: {str(e)}")


# Scrape Web From Movieku.CC
@app.on_message(filters.command(["movieku"], COMMAND_HANDLER))
@capture_err
async def movikucc(_, msg):
    m = await msg.reply("**__⏳ Please wait, scraping data ...__**", True)
    data = []
    if len(msg.command) == 1:
        try:
            html = await http.get(f"https://107.152.37.223/")
            r = BeautifulSoup(html.text, "lxml")
            res = r.find_all(class_="bx")
            for i in res:
                judul = i.find_all("a")[0]["title"]
                link = i.find_all("a")[0]["href"]
                data.append({"judul": judul, "link": link})
            if not data:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#Movieku Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
            msgs = ""
            for c, i in enumerate(data, start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            LOGGER.error(e)
            await m.delete()
            await msg.reply(f"ERROR: {e}", True)
    else:
        title = msg.text.split(" ", 1)[1]
        try:
            html = await http.get(f"https://107.152.37.223/?s={title}")
            r = BeautifulSoup(html.text, "lxml")
            res = r.find_all(class_="bx")
            for i in res:
                judul = i.find_all("a")[0]["title"]
                link = i.find_all("a")[0]["href"]
                data.append({"judul": judul, "link": link})
            if not data:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#Movieku Results For:</b> <code>{title}</code>\n\n"
            msgs = ""
            for c, i in enumerate(data, start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            LOGGER.error(e)
            await m.delete()
            await msg.reply(f"ERROR: {e}", True)


@app.on_message(filters.command(["savefilm21"], COMMAND_HANDLER))
@capture_err
async def savefilm21(_, msg):
    SITE = "https://185.99.135.215"
    try:
        title = msg.text.split(" ", 1)[1]
    except:
        title = None
    m = await msg.reply("**__⏳ Please wait, scraping data...__**", True)
    data = []
    try:
        if title is not None:
            html = await http.get(f"{SITE}/?s={title}", headers=headers)
            bs4 = BeautifulSoup(html.text, "lxml")
            res = bs4.find_all(class_="entry-title")
            for i in res:
                pas = i.find_all("a")
                judul = pas[0].text
                link = pas[0]["href"]
                data.append({"judul": judul, "link": link})
            if not data:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#SaveFilm21 Results For:</b> <code>{title}</code>\n\n"
            msgs = ""
            for c, i in enumerate(data, start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        else:
            html = await http.get(SITE, headers=headers)
            bs4 = BeautifulSoup(html.text, "lxml")
            res = bs4.find_all(class_="entry-title")
            for i in res:
                pas = i.find_all("a")
                judul = pas[0].text
                link = pas[0]["href"]
                data.append({"judul": judul, "link": link})
            await m.delete()
            head = f"<b>#SaveFilm21 Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
            msgs = ""
            for c, i in enumerate(data, start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
    except Exception as e:
        await m.delete()
        LOGGER.error(e)
        await msg.reply(f"ERROR: {e}", True)


@app.on_message(filters.command(["melongmovie"], COMMAND_HANDLER))
@capture_err
async def melongmovie(_, msg):
    SITE = "http://167.99.31.48"
    try:
        judul = msg.text.split(" ", 1)[1]
    except IndexError:
        judul = None
    data = []
    m = await msg.reply("**__⏳ Please wait, scraping data ...__**", True)
    if judul is not None:
        try:
            html = await http.get(f"{SITE}/?s={judul}", headers=headers)
            bs4 = BeautifulSoup(html.text, "lxml")
            for res in bs4.select(".box"):
                dd = res.select("a")
                url = dd[0]["href"]
                title = dd[0]["title"]
                try:
                    quality = dd[0].find(class_="quality").text
                except:
                    quality = "N/A"
                data.append({"judul": title, "link": url, "quality": quality})
            if not data:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#MelongMovie Results For:</b> <code>{judul}</code>\n\n"
            msgs = ""
            for c, i in enumerate(data, start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Quality:</b> {i['quality']}\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            await m.delete()
            LOGGER.error(e)
            await msg.reply(str(e), True)
    else:
        try:
            html = await http.get(SITE, headers=headers)
            bs4 = BeautifulSoup(html.text, "lxml")
            for res in bs4.select(".box"):
                dd = res.select("a")
                url = dd[0]["href"]
                title = dd[0]["title"]
                try:
                    quality = dd[0].find(class_="quality").text
                except:
                    quality = "N/A"
                data.append({"judul": title, "link": url, "quality": quality})
            if not data:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#MelongMovie Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
            msgs = ""
            for c, i in enumerate(data, start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Quality:</b> {i['quality']}\n<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            await m.delete()
            LOGGER.error(e)
            await msg.reply(str(e), True)


@app.on_message(filters.command(["pahe"], COMMAND_HANDLER))
@capture_err
async def pahe_scrap(_, msg):
    title = msg.text.split(" ", 1)[1] if len(msg.command) > 1 else ""
    m = await msg.reply("**__⏳ Please wait, scraping data..__**", True)
    try:
        api = await http.get(f"https://yasirapi.eu.org/pahe?q={title}")
        res = api.json()
        if not res["result"]:
            await m.delete()
            return await msg.reply("404 Result not FOUND!", True)
        head = f"<b>#Pahe Results For:</b> <code>{title}</code>\n\n" if title else f"<b>#Pahe Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
        await m.delete()
        msgs = ""
        for c, i in enumerate(res["result"], start=1):
            msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n\n"
            if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
                await asyncio.sleep(2)
                msgs = ""
        if msgs != "":
            await msg.reply(
                head + msgs,
                True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="❌ Close",
                                callback_data=f"close#{msg.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
    except Exception as e:
        await m.delete()
        LOGGER.error(e)
        await msg.reply(f"ERROR: {e}", True)


@app.on_message(filters.command(["terbit21"], COMMAND_HANDLER))
@capture_err
async def terbit21_scrap(_, msg):
    m = await msg.reply("**__Checking data list ...__**", True)
    if len(msg.command) == 1:
        try:
            r = await http.get("https://yasirapi.eu.org/terbit21")
            res = r.json()
            if not res["result"]:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#Terbit21 Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
            msgs = ""
            for c, i in enumerate(res["result"], start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
                msgs += f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n" if not re.search(r"Complete|Ongoing", i["kategori"]) else "\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            await m.delete()
            LOGGER.error(e)
            await msg.reply(str(e), True)
    else:
        try:
            title = msg.text.split(" ", 1)[1]
            r = await http.get(f"https://yasirapi.eu.org/terbit21?q={title}")
            res = r.json()
            if not res["result"]:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#Terbit21 Results For:</b> <code>{title}</code>\n\n"
            msgs = ""
            for c, i in enumerate(res["result"], start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
                msgs += f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n" if not re.search(r"Complete|Ongoing", i["kategori"]) else "\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            await m.delete()
            LOGGER.error(e)
            await msg.reply(str(e), True)


@app.on_message(filters.command(["lk21"], COMMAND_HANDLER))
@capture_err
async def lk21_scrap(_, msg):
    m = await msg.reply("**__Checking data list ...__**", True)
    if len(msg.command) == 1:
        try:
            r = await http.get("https://yasirapi.eu.org/lk21")
            res = r.json()
            if res.get("detail", None):
                await m.delete()
                return await msg.reply(f"ERROR: {res['detail']}", True)
            if not res["result"]:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#Layarkaca21 Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
            msgs = ""
            for c, i in enumerate(res["result"], start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
                msgs += f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n" if not re.search(r"Complete|Ongoing", i["kategori"]) else "\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            await m.delete()
            LOGGER.error(e)
            await msg.reply(str(e), True)
    else:
        try:
            title = msg.text.split(" ", 1)[1]
            r = await http.get(f"https://yasirapi.eu.org/lk21?q={title}")
            res = r.json()
            if res.get("detail", None):
                await m.delete()
                return await msg.reply(f"ERROR: {res['detail']}", True)
            if not res["result"]:
                await m.delete()
                return await msg.reply("404 Result not FOUND!", True)
            await m.delete()
            head = f"<b>#Layarkaca21 Results For:</b> <code>{title}</code>\n\n"
            msgs = ""
            for c, i in enumerate(res["result"], start=1):
                msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Category:</b> <code>{i['kategori']}</code>\n"
                msgs += f"💠 <b><a href='{i['dl']}'>Download</a></b>\n\n" if not re.search(r"Complete|Ongoing", i["kategori"]) else "\n"
                if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                    await msg.reply(
                        head + msgs,
                        True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="❌ Close",
                                        callback_data=f"close#{msg.from_user.id}",
                                    )
                                ]
                            ]
                        ),
                    )
                    await asyncio.sleep(2)
                    msgs = ""
            if msgs != "":
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
        except Exception as e:
            await m.delete()
            LOGGER.error(e)
            await msg.reply(str(e), True)


@app.on_message(filters.command(["gomov"], COMMAND_HANDLER))
@capture_err
async def gomov_scrap(_, msg):
    m = await msg.reply("**__⏳ Please wait, scraping data ...__**", True)
    try:
        title = msg.text.split(" ", 1)[1]
    except IndexError:
        title = ""
    try:
        html = await http.get(f"https://185.173.38.216/?s={title}", headers=headers)
        text = BeautifulSoup(html.text, "lxml")
        entry = text.find_all(class_="entry-header")
        if "Nothing Found" in entry[0].text:
            await m.delete()
            if title != "":
                await msg.reply(f"404 Not FOUND For: {title}", True)
            else:
                await msg.reply(f"404 Not FOUND!", True)
            return
        data = []
        for i in entry:
            genre = i.find(class_="gmr-movie-on").text
            genre = f"{genre}" if genre != "" else "N/A"
            judul = i.find(class_="entry-title").find("a").text
            link = i.find(class_="entry-title").find("a").get("href")
            data.append({"judul": judul, "link": link, "genre": genre})
        if title != "":
            head = f"<b>#Gomov Results For:</b> <code>{title}</code>\n\n"
        else:
            head = f"<b>#Gomov Latest:</b>\n🌀 Use /{msg.command[0]} [title] to start search with title.\n\n"
        msgs = ""
        await m.delete()
        for c, i in enumerate(data, start=1):
            msgs += f"<b>{c}. <a href='{i['link']}'>{i['judul']}</a></b>\n<b>Genre:</b> <code>{i['genre']}</code>\n"
            msgs += f"<b>Extract:</b> <code>/{msg.command[0]}_scrap {i['link']}</code>\n\n" if not re.search(r"Series", i["genre"]) else "\n"
            if len(head.encode("utf-8") + msgs.encode("utf-8")) >= 4000:
                await msg.reply(
                    head + msgs,
                    True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="❌ Close",
                                    callback_data=f"close#{msg.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
                await asyncio.sleep(2)
                msgs = ""
        if msgs != "":
            await msg.reply(
                head + msgs,
                True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="❌ Close",
                                callback_data=f"close#{msg.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
    except Exception as e:
        LOGGER.error(e)
        await m.delete()
        await msg.reply(f"ERROR: <code>{e}</code>", True)


@app.on_message(filters.command(["savefilm21_scrap"], COMMAND_HANDLER))
@capture_err
async def savefilm21_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}

        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="button button-shadow")
        res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
        await message.reply(
            f"<b>Hasil Scrap dari {link}</b>:\n\n{res}",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❌ Close",
                            callback_data=f"close#{message.from_user.id}",
                        )
                    ]
                ]
            ),
        )
    except IndexError:
        return await message.reply(f"Gunakan command /{message.command[0]} <b>[link]</b> untuk scrap link download")
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


@app.on_message(filters.command(["nodrakor_scrap"], COMMAND_HANDLER))
@capture_err
async def nodrakor_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}

        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        hasil = soup.find_all(class_="gmr-download-wrap clearfix")[0]
        await message.reply(f"<b>Hasil Scrap dari {link}</b>:\n{hasil}")
    except IndexError:
        return await message.reply(f"Gunakan command /{message.command[0]} <b>[link]</b> untuk scrap link download")
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


# Scrape Link Download Movieku.CC
@app.on_message(filters.command(["movieku_scrap"], COMMAND_HANDLER))
@capture_err
async def muviku_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}

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


@app.on_message(filters.command(["melongmovie_scrap"], COMMAND_HANDLER))
@capture_err
async def melong_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}

        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        for ep in soup.findAll(text=re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
            hardsub = ep.findPrevious("div")
            softsub = ep.findNext("div")
            rep = f"{hardsub}\n{softsub}"
            await message.reply(rep)
    except IndexError:
        await message.reply(f"Gunakan command /{message.command[0]} <b>[link]</b> untuk scrap link download")


@app.on_message(filters.command(["gomov_scrap", "zonafilm_scrap"], COMMAND_HANDLER))
@capture_err
async def gomov_zonafilm_dl(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}

        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        entry = soup.find(class_="gmr-download-wrap clearfix")
        hasil = soup.find(class_="title-download").text
        for i in entry.find(class_="list-inline gmr-download-list clearfix"):
            title = i.find("a").text
            link = i.find("a")["href"]
            hasil += f"\n{title}\n{link}\n"
        await message.reply(
            hasil,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❌ Close",
                            callback_data=f"close#{message.from_user.id}",
                        )
                    ]
                ]
            ),
        )
    except IndexError:
        await message.reply(f"Gunakan command /{message.command[0]} <b>[link]</b> untuk scrap link download")
