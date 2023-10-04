# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import httpx
import json
import logging
import re
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import Client, enums
from pyrogram.errors import (
    MediaCaptionTooLong,
    MediaEmpty,
    MessageIdInvalid,
    MessageNotModified,
    PhotoInvalidDimensions,
    WebpageCurlFailed,
    WebpageMediaEmpty,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from database.imdb_db import add_imdbset, is_imdbset, remove_imdbset
from misskaty import app
from misskaty.helper import GENRES_EMOJI, Cache, fetch, get_random_string, search_jw
from utils import demoji

LOGGER = logging.getLogger("MissKaty")
LIST_CARI = Cache(filename="imdb_cache.db", path="cache", in_memory=False)


# IMDB Choose Language
@app.on_cmd("imdb")
async def imdb_choose(_, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(
            f"ℹ️ Please add query after CMD!\nEx: <code>/{ctx.command[0]} Jurassic World</code>",
            del_in=7,
        )
    if ctx.sender_chat:
        return await ctx.reply_msg(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    kuery = ctx.text.split(None, 1)[1]
    is_imdb, lang = await is_imdbset(ctx.from_user.id)
    if is_imdb:
        if lang == "eng":
            return await imdb_search_en(kuery, ctx)
        else:
            return await imdb_search_id(kuery, ctx)
    buttons = InlineKeyboard()
    ranval = get_random_string(4)
    LIST_CARI.add(ranval, kuery, timeout=30)
    buttons.row(
        InlineButton("🇺🇸 English", f"imdbcari#eng#{ranval}#{ctx.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"imdbcari#ind#{ranval}#{ctx.from_user.id}"),
    )
    buttons.row(InlineButton("🚩 Set Default Language", f"imdbset#{ctx.from_user.id}"))
    buttons.row(InlineButton("❌ Close", f"close#{ctx.from_user.id}"))
    await ctx.reply_photo(
        "https://img.yasirweb.eu.org/file/270955ef0d1a8a16831a9.jpg",
        caption=f"Hi {ctx.from_user.mention}, Please select the language you want to use on IMDB Search. If you want use default lang for every user, click third button. So no need click select lang if use CMD.",
        reply_markup=buttons,
        quote=True,
    )


@app.on_cb("imdbset")
async def imdblangset(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    buttons = InlineKeyboard()
    buttons.row(
        InlineButton("🇺🇸 English", f"setimdb#eng#{query.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"setimdb#ind#{query.from_user.id}"),
    )
    is_imdb, _ = await is_imdbset(query.from_user.id)
    if is_imdb:
        buttons.row(
            InlineButton("🗑 Remove UserSetting", f"setimdb#rm#{query.from_user.id}")
        )
    buttons.row(InlineButton("❌ Close", f"close#{query.from_user.id}"))
    try:
        await query.message.edit_caption(
            "<i>Please select available language below..</i>", reply_markup=buttons
        )
    except (MessageIdInvalid, MessageNotModified):
        pass


@app.on_cb("setimdb")
async def imdbsetlang(_, query: CallbackQuery):
    _, lang, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    _, langset = await is_imdbset(query.from_user.id)
    if langset == lang:
        return await query.answer(f"⚠️ Your Setting Already in ({langset})!", True)
    try:
        if lang == "eng":
            await add_imdbset(query.from_user.id, lang)
            await query.message.edit_caption(
                "Language interface for IMDB has been changed to English."
            )
        elif lang == "ind":
            await add_imdbset(query.from_user.id, lang)
            await query.message.edit_caption(
                "Bahasa tampilan IMDB sudah diubah ke Indonesia."
            )
        else:
            await remove_imdbset(query.from_user.id)
            await query.message.edit_caption(
                "UserSetting for IMDB has been deleted from database."
            )
    except (MessageIdInvalid, MessageNotModified):
        pass


async def imdb_search_id(kueri, message):
    BTN = []
    k = await message.reply_photo(
        "https://img.yasirweb.eu.org/file/270955ef0d1a8a16831a9.jpg",
        caption=f"🔎 Menelusuri <code>{kueri}</code> di database IMDb ...",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await fetch.get(
            f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json"
        )
        r.raise_for_status()
        res = r.json().get("d")
        if not res:
            return await k.edit_caption(
                f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>"
            )
        msg += f"🎬 Ditemukan ({len(res)}) hasil untuk kueri: <code>{kueri}</code>\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("l")
            if year := movie.get("yr"):
                year = f"({year})"
            elif year := movie.get("y"):
                year = f"({year})"
            else:
                year = "(N/A)"
            typee = movie.get("q", "N/A").replace("feature", "movie").title()
            movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
            msg += f"{num}. {title} {year} - {typee}\n"
            BTN.append(
                InlineKeyboardButton(
                    text=num,
                    callback_data=f"imdbres_id#{message.from_user.id}#{movieID}",
                )
            )
        BTN.extend(
            (
                InlineKeyboardButton(
                    text="🚩 Language",
                    callback_data=f"imdbset#{message.from_user.id}",
                ),
                InlineKeyboardButton(
                    text="❌ Close",
                    callback_data=f"close#{message.from_user.id}",
                ),
            )
        )
        buttons.add(*BTN)
        await k.edit_caption(msg, reply_markup=buttons)
    except httpx.HTTPError as exc:
        await k.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>", disable_web_page_preview=True)
    except (MessageIdInvalid, MessageNotModified):
        pass
    except Exception as err:
        await k.edit_caption(
            f"Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>"
        )


async def imdb_search_en(kueri, message):
    BTN = []
    k = await message.reply_photo(
        "https://img.yasirweb.eu.org/file/270955ef0d1a8a16831a9.jpg",
        caption=f"🔎 Searching <code>{kueri}</code> in IMDb Database...",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await fetch.get(
            f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json"
        )
        r.raise_for_status()
        res = r.json().get("d")
        if not res:
            return await k.edit_caption(
                f"⛔️ Result not found for keywords: <code>{kueri}</code>"
            )
        msg += f"🎬 Found ({len(res)}) result for keywords: <code>{kueri}</code>\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("l")
            if year := movie.get("yr"):
                year = f"({year})"
            elif year := movie.get("y"):
                year = f"({year})"
            else:
                year = "(N/A)"
            typee = movie.get("q", "N/A").replace("feature", "movie").title()
            movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
            msg += f"{num}. {title} {year} - {typee}\n"
            BTN.append(
                InlineKeyboardButton(
                    text=num,
                    callback_data=f"imdbres_en#{message.from_user.id}#{movieID}",
                )
            )
        BTN.extend(
            (
                InlineKeyboardButton(
                    text="🚩 Language",
                    callback_data=f"imdbset#{message.from_user.id}",
                ),
                InlineKeyboardButton(
                    text="❌ Close",
                    callback_data=f"close#{message.from_user.id}",
                ),
            )
        )
        buttons.add(*BTN)
        await k.edit_caption(msg, reply_markup=buttons)
    except httpx.HTTPError as exc:
        await k.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>", disable_web_page_preview=True)
    except (MessageIdInvalid, MessageNotModified):
        pass
    except Exception as err:
        await k.edit_caption(
            f"Failed when requesting movies title. Maybe got rate limit or down.\n\n<b>ERROR:</b> <code>{err}</code>"
        )


@app.on_cb("imdbcari")
async def imdbcari(_, query: CallbackQuery):
    BTN = []
    _, lang, msg, uid = query.data.split("#")
    if lang == "ind":
        if query.from_user.id != int(uid):
            return await query.answer("⚠️ Akses Ditolak!", True)
        try:
            kueri = LIST_CARI.get(msg)
            del LIST_CARI[msg]
        except KeyError:
            return await query.message.edit_caption("⚠️ Callback Query Sudah Expired!")
        try:
            await query.message.edit_caption(
                "<i>🔎 Sedang mencari di Database IMDB..</i>"
            )
        except (MessageIdInvalid, MessageNotModified):
            pass
        msg = ""
        buttons = InlineKeyboard(row_width=4)
        try:
            r = await fetch.get(
                f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json"
            )
            r.raise_for_status()
            res = r.json().get("d")
            if not res:
                return await query.message.edit_caption(
                    f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>"
                )
            msg += f"🎬 Ditemukan ({len(res)}) hasil dari: <code>{kueri}</code> ~ {query.from_user.mention}\n\n"
            for num, movie in enumerate(res, start=1):
                title = movie.get("l")
                if year := movie.get("yr"):
                    year = f"({year})"
                elif year := movie.get("y"):
                    year = f"({year})"
                else:
                    year = "(N/A)"
                typee = movie.get("q", "N/A").replace("feature", "movie").title()
                movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
                msg += f"{num}. {title} {year} - {typee}\n"
                BTN.append(
                    InlineKeyboardButton(
                        text=num, callback_data=f"imdbres_id#{uid}#{movieID}"
                    )
                )
            BTN.extend(
                (
                    InlineKeyboardButton(
                        text="🚩 Language", callback_data=f"imdbset#{uid}"
                    ),
                    InlineKeyboardButton(text="❌ Close", callback_data=f"close#{uid}"),
                )
            )
            buttons.add(*BTN)
            await query.message.edit_caption(msg, reply_markup=buttons)
        except httpx.HTTPError as exc:
            await query.message.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>", disable_web_page_preview=True)
        except (MessageIdInvalid, MessageNotModified):
            pass
        except Exception as err:
            await query.message.edit_caption(
                f"Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>"
            )
    else:
        if query.from_user.id != int(uid):
            return await query.answer("⚠️ Access Denied!", True)
        try:
            kueri = LIST_CARI.get(msg)
            del LIST_CARI[msg]
        except KeyError:
            return await query.message.edit_caption("⚠️ Callback Query Expired!")
        await query.message.edit_caption("<i>🔎 Looking in the IMDB Database..</i>")
        msg = ""
        buttons = InlineKeyboard(row_width=4)
        try:
            r = await fetch.get(
                f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json"
            )
            r.raise_for_status()
            res = r.json().get("d")
            if not res:
                return await query.message.edit_caption(
                    f"⛔️ Result not found for keywords: <code>{kueri}</code>"
                )
            msg += f"🎬 Found ({len(res)}) result for keywords: <code>{kueri}</code> ~ {query.from_user.mention}\n\n"
            for num, movie in enumerate(res, start=1):
                title = movie.get("l")
                if year := movie.get("yr"):
                    year = f"({year})"
                elif year := movie.get("y"):
                    year = f"({year})"
                else:
                    year = "(N/A)"
                typee = movie.get("q", "N/A").replace("feature", "movie").title()
                movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
                msg += f"{num}. {title} {year} - {typee}\n"
                BTN.append(
                    InlineKeyboardButton(
                        text=num, callback_data=f"imdbres_en#{uid}#{movieID}"
                    )
                )
            BTN.extend(
                (
                    InlineKeyboardButton(
                        text="🚩 Language", callback_data=f"imdbset#{uid}"
                    ),
                    InlineKeyboardButton(text="❌ Close", callback_data=f"close#{uid}"),
                )
            )
            buttons.add(*BTN)
            await query.message.edit_caption(msg, reply_markup=buttons)
        except httpx.HTTPError as exc:
            await query.message.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>", disable_web_page_preview=True)
        except (MessageIdInvalid, MessageNotModified):
            pass
        except Exception as err:
            await query.message.edit_caption(
                f"Failed when requesting movies title. Maybe got rate limit or down.\n\n<b>ERROR:</b> <code>{err}</code>"
            )


@app.on_cb("imdbres_id")
async def imdb_id_callback(self: Client, query: CallbackQuery):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    try:
        await query.message.edit_caption("⏳ Permintaan kamu sedang diproses.. ")
        imdb_url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await fetch.get(imdb_url)
        resp.raise_for_status()
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(
            sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
        )
        ott = await search_jw(r_json.get("name"), "ID")
        typee = r_json.get("@type", "")
        res_str = ""
        tahun = (
            re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0]
            if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)
            else "N/A"
        )
        res_str += f"<b>📹 Judul:</b> <a href='{imdb_url}'>{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n"
        if aka := r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
        else:
            res_str += "\n"
        if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = (
                durasi[0].find(class_="ipc-metadata-list-item__content-container").text
            )
            res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
        if kategori := r_json.get("contentRating"):
            res_str += f"<b>Kategori:</b> <code>{kategori}</code> \n"
        if rating := r_json.get("aggregateRating"):
            res_str += f"<b>Peringkat:</b> <code>{rating['ratingValue']}⭐️ dari {rating['ratingCount']} pengguna</code>\n"
        if release := sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = (
                release[0]
                .find(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
                .text
            )
            rilis_url = release[0].find(
                class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
            )["href"]
            res_str += (
                f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
            )
        if genre := r_json.get("genre"):
            genre = "".join(
                f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                if i in GENRES_EMOJI
                else f"#{i.replace('-', '_').replace(' ', '_')}, "
                for i in r_json["genre"]
            )
            res_str += f"<b>Genre:</b> {genre[:-2]}\n"
        if negara := sop.select('li[data-testid="title-details-origin"]'):
            country = "".join(
                f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, "
                for country in negara[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
            res_str += f"<b>Negara:</b> {country[:-2]}\n"
        if bahasa := sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(
                f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                for lang in bahasa[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
            res_str += f"<b>Bahasa:</b> {language[:-2]}\n"
        res_str += "\n<b>🙎 Info Cast:</b>\n"
        if directors := r_json.get("director"):
            director = "".join(
                f"<a href='{i['url']}'>{i['name']}</a>, " for i in directors
            )
            res_str += f"<b>Sutradara:</b> {director[:-2]}\n"
        if creators := r_json.get("creator"):
            creator = "".join(
                f"<a href='{i['url']}'>{i['name']}</a>, "
                for i in creators
                if i["@type"] == "Person"
            )
            res_str += f"<b>Penulis:</b> {creator[:-2]}\n"
        if actors := r_json.get("actor"):
            actor = "".join(f"<a href='{i['url']}'>{i['name']}</a>, " for i in actors)
            res_str += f"<b>Pemeran:</b> {actor[:-2]}\n\n"
        if deskripsi := r_json.get("description"):
            summary = GoogleTranslator("auto", "id").translate(deskripsi)
            res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
        if keywd := r_json.get("keywords"):
            key_ = "".join(
                f"#{i.replace(' ', '_').replace('-', '_')}, " for i in keywd.split(",")
            )
            res_str += f"<b>🔥 Kata Kunci:</b> {key_[:-2]} \n"
        if award := sop.select('li[data-testid="award_information"]'):
            awards = (
                award[0].find(class_="ipc-metadata-list-item__list-content-item").text
            )
            res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(awards)}</code>\n"
        else:
            res_str += "\n"
        if ott != "":
            res_str += f"Tersedia di:\n{ott}\n"
        res_str += f"<b>©️ IMDb by</b> @{self.me.username}"
        if trailer := r_json.get("trailer"):
            trailer_url = trailer["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=imdb_url),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)]]
            )
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(
                    InputMediaPhoto(
                        thumb, caption=res_str, parse_mode=enums.ParseMode.HTML
                    ),
                    reply_markup=markup,
                )
            except (PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(
                    InputMediaPhoto(
                        poster, caption=res_str, parse_mode=enums.ParseMode.HTML
                    ),
                    reply_markup=markup,
                )
            except (
                MediaEmpty,
                MediaCaptionTooLong,
                WebpageCurlFailed,
                MessageNotModified,
            ):
                await query.message.reply(
                    res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup
                )
            except Exception as err:
                LOGGER.error(f"Terjadi error saat menampilkan data IMDB. ERROR: {err}")
        else:
            await query.message.edit_caption(
                res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup
            )
    except httpx.HTTPError as exc:
        await query.message.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>", disable_web_page_preview=True)
    except AttributeError:
        await query.message.edit_caption("Maaf, gagal mendapatkan info data dari IMDB.")
    except (MessageNotModified, MessageIdInvalid):
        pass


@app.on_cb("imdbres_en")
async def imdb_en_callback(self: Client, query: CallbackQuery):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    try:
        await query.message.edit_caption("<i>⏳ Getting IMDb source..</i>")
        imdb_url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await fetch.get(imdb_url)
        resp.raise_for_status()
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(
            sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
        )
        ott = await search_jw(r_json.get("name"), "US")
        typee = r_json.get("@type", "")
        res_str = ""
        tahun = (
            re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0]
            if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)
            else "N/A"
        )
        res_str += f"<b>📹 Judul:</b> <a href='{imdb_url}'>{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n"
        if aka := r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
        else:
            res_str += "\n"
        if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = (
                durasi[0].find(class_="ipc-metadata-list-item__content-container").text
            )
            res_str += f"<b>Duration:</b> <code>{durasi}</code>\n"
        if kategori := r_json.get("contentRating"):
            res_str += f"<b>Category:</b> <code>{kategori}</code> \n"
        if rating := r_json.get("aggregateRating"):
            res_str += f"<b>Rating:</b> <code>{rating['ratingValue']}⭐️ from {rating['ratingCount']} users</code>\n"
        if release := sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = (
                release[0]
                .find(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
                .text
            )
            rilis_url = release[0].find(
                class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
            )["href"]
            res_str += (
                f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
            )
        if genre := r_json.get("genre"):
            genre = "".join(
                f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                if i in GENRES_EMOJI
                else f"#{i.replace('-', '_').replace(' ', '_')}, "
                for i in r_json["genre"]
            )
            res_str += f"<b>Genre:</b> {genre[:-2]}\n"
        if negara := sop.select('li[data-testid="title-details-origin"]'):
            country = "".join(
                f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, "
                for country in negara[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
            res_str += f"<b>Country:</b> {country[:-2]}\n"
        if bahasa := sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(
                f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                for lang in bahasa[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
            res_str += f"<b>Language:</b> {language[:-2]}\n"
        res_str += "\n<b>🙎 Cast Info:</b>\n"
        if r_json.get("director"):
            director = "".join(
                f"<a href='{i['url']}'>{i['name']}</a>, " for i in r_json["director"]
            )
            res_str += f"<b>Director:</b> {director[:-2]}\n"
        if r_json.get("creator"):
            creator = "".join(
                f"<a href='{i['url']}'>{i['name']}</a>, "
                for i in r_json["creator"]
                if i["@type"] == "Person"
            )
            res_str += f"<b>Writer:</b> {creator[:-2]}\n"
        if r_json.get("actor"):
            actors = actors = "".join(
                f"<a href='{i['url']}'>{i['name']}</a>, " for i in r_json["actor"]
            )
            res_str += f"<b>Stars:</b> {actors[:-2]}\n\n"
        if description := r_json.get("description"):
            res_str += f"<b>📜 Summary: </b> <code>{description}</code>\n\n"
        if r_json.get("keywords"):
            key_ = "".join(
                f"#{i.replace(' ', '_').replace('-', '_')}, "
                for i in r_json["keywords"].split(",")
            )
            res_str += f"<b>🔥 Keywords:</b> {key_[:-2]} \n"
        if award := sop.select('li[data-testid="award_information"]'):
            awards = (
                award[0].find(class_="ipc-metadata-list-item__list-content-item").text
            )
            res_str += f"<b>🏆 Awards:</b> <code>{awards}</code>\n"
        else:
            res_str += "\n"
        if ott != "":
            res_str += f"Available On:\n{ott}\n"
        res_str += f"<b>©️ IMDb by</b> @{self.me.username}"
        if trailer := r_json.get("trailer"):
            trailer_url = trailer["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=imdb_url),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)]]
            )
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(
                    InputMediaPhoto(
                        thumb, caption=res_str, parse_mode=enums.ParseMode.HTML
                    ),
                    reply_markup=markup,
                )
            except (PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(
                    InputMediaPhoto(
                        poster, caption=res_str, parse_mode=enums.ParseMode.HTML
                    ),
                    reply_markup=markup,
                )
            except (
                MediaCaptionTooLong,
                WebpageCurlFailed,
                MediaEmpty,
                MessageNotModified,
            ):
                await query.message.reply(
                    res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup
                )
            except Exception as err:
                LOGGER.error(f"Error while displaying IMDB Data. ERROR: {err}")
        else:
            await query.message.edit_caption(
                res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup
            )
    except httpx.HTTPError as exc:
        await query.message.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>", disable_web_page_preview=True)
    except AttributeError:
        await query.message.edit_caption("Sorry, failed getting data from IMDB.")
    except (MessageNotModified, MessageIdInvalid):
        pass
