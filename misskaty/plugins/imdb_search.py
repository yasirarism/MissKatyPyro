import json
import logging
import re
import traceback

from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from utils import demoji
from deep_translator import GoogleTranslator
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import filters, enums
from pyrogram.errors import (
    MediaEmpty,
    MessageNotModified,
    PhotoInvalidDimensions,
    WebpageMediaEmpty,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from database.imdb_db import *
from misskaty import BOT_USERNAME, app
from misskaty.core.message_utils import *
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import http, get_random_string, search_jw, GENRES_EMOJI, post_to_telegraph
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL

LOGGER = logging.getLogger(__name__)
LIST_CARI = {}
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"}


# IMDB Choose Language
@app.on_message(filters.command(["imdb"], COMMAND_HANDLER))
@capture_err
@ratelimiter
async def imdb_choose(_, m):
    if len(m.command) == 1:
        return await kirimPesan(m, f"ℹ️ Please add query after CMD!\nEx: <code>/{m.command[0]} Jurassic World</code>")
    if m.sender_chat:
        return await kirimPesan(m, "This feature not supported for channel..")
    kuery = m.text.split(None, 1)[1]
    is_imdb, lang = await is_imdbset(m.from_user.id)
    if is_imdb:
        if lang == "eng":
            return await imdb_search_en(kuery, m)
        else:
            return await imdb_search_id(kuery, m)
    buttons = InlineKeyboard()
    ranval = get_random_string(4)
    LIST_CARI[ranval] = kuery
    buttons.row(
        InlineButton("🇺🇸 English", f"imdbcari#eng#{ranval}#{m.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"imdbcari#ind#{ranval}#{m.from_user.id}"),
    )
    buttons.row(InlineButton("🚩 Set Default Language", f"imdbset#{m.from_user.id}"))
    buttons.row(InlineButton("❌ Close", f"close#{m.from_user.id}"))
    await m.reply_photo(
        "https://telegra.ph/file/270955ef0d1a8a16831a9.jpg",
        caption=f"Hi {m.from_user.mention}, Please select the language you want to use on IMDB Search. If you want use default lang for every user, click third button. So no need click select lang if use CMD.",
        reply_markup=buttons,
        quote=True,
    )


@app.on_callback_query(filters.regex("^imdbset"))
@ratelimiter
async def imdbsetlang(client, query):
    i, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    buttons = InlineKeyboard()
    buttons.row(
        InlineButton("🇺🇸 English", f"setimdb#eng#{query.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"setimdb#ind#{query.from_user.id}"),
    )
    is_imdb, lang = await is_imdbset(query.from_user.id)
    if is_imdb:
        buttons.row(InlineButton("🗑 Remove UserSetting", f"setimdb#rm#{query.from_user.id}"))
    buttons.row(InlineButton("❌ Close", f"close#{query.from_user.id}"))
    await query.message.edit_caption("<i>Please select available language below..</i>", reply_markup=buttons)


@app.on_callback_query(filters.regex("^setimdb"))
@ratelimiter
async def imdbsetlang(client, query):
    i, lang, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    if lang == "eng":
        await add_imdbset(query.from_user.id, lang)
        await query.message.edit_caption("Language interface for IMDB has been changed to English.")
    elif lang == "ind":
        await add_imdbset(query.from_user.id, lang)
        await query.message.edit_caption("Bahasa tampilan IMDB sudah diubah ke Indonesia.")
    else:
        await remove_imdbset(query.from_user.id)
        await query.message.edit_caption("UserSetting for IMDB has been deleted from database.")


async def imdb_search_id(kueri, message):
    BTN = []
    k = await message.reply_photo(
        "https://telegra.ph/file/270955ef0d1a8a16831a9.jpg",
        caption=f"🔎 Menelusuri <code>{kueri}</code> di database IMDb ...",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await http.get(f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json", headers=headers)
        res = r.json().get("d")
        if not res:
            return await k.edit_caption(f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>")
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
    except Exception as err:
        await k.edit_caption(f"Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>")


async def imdb_search_en(kueri, message):
    BTN = []
    k = await message.reply_photo(
        "https://telegra.ph/file/270955ef0d1a8a16831a9.jpg",
        caption=f"🔎 Searching <code>{kueri}</code> in IMDb Database...",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await http.get(f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json", headers=headers)
        res = r.json().get("d")
        if not res:
            return await k.edit_caption(f"⛔️ Result not found for keywords: <code>{kueri}</code>")
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
    except Exception as err:
        await k.edit_caption(f"Failed when requesting movies title. Maybe got rate limit or down.\n\n<b>ERROR:</b> <code>{err}</code>")


@app.on_callback_query(filters.regex("^imdbcari"))
@ratelimiter
async def imdbcari(client, query):
    BTN = []
    i, lang, msg, uid = query.data.split("#")
    if lang == "ind":
        if query.from_user.id != int(uid):
            return await query.answer("⚠️ Akses Ditolak!", True)
        try:
            kueri = LIST_CARI.get(msg)
            del LIST_CARI[msg]
        except KeyError:
            return await query.message.edit_caption("⚠️ Callback Query Sudah Expired!")
        await query.message.edit_caption("<i>🔎 Sedang mencari di Database IMDB..</i>")
        msg = ""
        buttons = InlineKeyboard(row_width=4)
        try:
            r = await http.get(f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json", headers=headers)
            res = r.json().get("d")
            if not res:
                return await query.message.edit_caption(f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>")
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
                BTN.append(InlineKeyboardButton(text=num, callback_data=f"imdbres_id#{uid}#{movieID}"))
            BTN.extend(
                (
                    InlineKeyboardButton(text="🚩 Language", callback_data=f"imdbset#{uid}"),
                    InlineKeyboardButton(text="❌ Close", callback_data=f"close#{uid}"),
                )
            )
            buttons.add(*BTN)
            await query.message.edit_caption(msg, reply_markup=buttons)
        except Exception as err:
            await query.message.edit_caption(f"Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>")
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
            r = await http.get(f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json", headers=headers)
            res = r.json().get("d")
            if not res:
                return await query.message.edit_caption(f"⛔️ Result not found for keywords: <code>{kueri}</code>")
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
                BTN.append(InlineKeyboardButton(text=num, callback_data=f"imdbres_en#{uid}#{movieID}"))
            BTN.extend(
                (
                    InlineKeyboardButton(text="🚩 Language", callback_data=f"imdbset#{uid}"),
                    InlineKeyboardButton(text="❌ Close", callback_data=f"close#{uid}"),
                )
            )
            buttons.add(*BTN)
            await query.message.edit_caption(msg, reply_markup=buttons)
        except Exception as err:
            await query.message.edit_caption(f"Failed when requesting movies title. Maybe got rate limit or down.\n\n<b>ERROR:</b> <code>{err}</code>")


@app.on_callback_query(filters.regex("^imdbres_id"))
@ratelimiter
async def imdb_id_callback(_, query):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    try:
        await query.message.edit_caption("⏳ Permintaan kamu sedang diproses.. ")
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await http.get(url, headers=headers)
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(sop.find("script", attrs={"type": "application/ld+json"}).contents[0])
        ott = await search_jw(r_json.get("name"), "ID")
        typee = r_json.get("@type", "")
        res_str = ""
        tahun = re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0] if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text) else "N/A"
        res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n"
        if aka := r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
        else:
            res_str += "\n"
        if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = durasi[0].find(class_="ipc-metadata-list-item__content-container").text
            res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
        if kategori := r_json.get("contentRating"):
            res_str += f"<b>Kategori:</b> <code>{kategori}</code> \n"
        if rating := r_json.get("aggregateRating"):
            res_str += f"<b>Peringkat:</b> <code>{rating['ratingValue']}⭐️ dari {rating['ratingCount']} pengguna</code>\n"
        if release := sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = release[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
            rilis_url = release[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")["href"]
            res_str += f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
        if genre := r_json.get("genre"):
            genre = "".join(f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, " if i in GENRES_EMOJI else f"#{i.replace('-', '_').replace(' ', '_')}, " for i in r_json["genre"])
            genre = genre[:-2]
            res_str += f"<b>Genre:</b> {genre}\n"
        if negara := sop.select('li[data-testid="title-details-origin"]'):
            country = "".join(f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, " for country in negara[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
            country = country[:-2]
            res_str += f"<b>Negara:</b> {country}\n"
        if bahasa := sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(f"#{lang.text.replace(' ', '_').replace('-', '_')}, " for lang in bahasa[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
            language = language[:-2]
            res_str += f"<b>Bahasa:</b> {language}\n"
        res_str += "\n<b>🙎 Info Cast:</b>\n"
        if directors := r_json.get("director"):
            director = ""
            for i in directors:
                name = i["name"]
                url = i["url"]
                director += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            director = director[:-2]
            res_str += f"<b>Sutradara:</b> {director}\n"
        if creators := r_json.get("creator"):
            creator = ""
            for i in creators:
                if i["@type"] == "Person":
                    name = i["name"]
                    url = i["url"]
                    creator += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            creator = creator[:-2]
            res_str += f"<b>Penulis:</b> {creator}\n"
        if actor := r_json.get("actor"):
            actors = ""
            for i in actor:
                name = i["name"]
                url = i["url"]
                actors += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            actors = actors[:-2]
            res_str += f"<b>Pemeran:</b> {actors}\n\n"
        if deskripsi := r_json.get("description"):
            summary = GoogleTranslator("auto", "id").translate(deskripsi)
            res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
        if keywd := r_json.get("keywords"):
            keywords = keywd.split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_").replace("-", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Kata Kunci:</b> {key_} \n"
        if award := sop.select('li[data-testid="award_information"]'):
            awards = award[0].find(class_="ipc-metadata-list-item__list-content-item").text
            res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(awards)}</code>\n"
        else:
            res_str += "\n"
        if ott != "":
            res_str += f"Tersedia di:\n{ott}\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if trailer := r_json.get("trailer"):
            trailer_url = trailer["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}")]])
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(InputMediaPhoto(thumb, caption=res_str, parse_mode=enums.ParseMode.HTML), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(InputMediaPhoto(poster, caption=res_str, parse_mode=enums.ParseMode.HTML), reply_markup=markup)
            except Exception:
                await query.message.edit_caption(res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
    except (MessageNotModified, MessageIdInvalid):
        pass
    except Exception as exc:
        err = traceback.format_exc(limit=20)
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>\n<b>Full Error:</b> <code>{err}</code>\n\nSilahkan lapor ke owner detail errornya dengan lengkap, atau laporan error akan diabaikan.")
        await app.send_message(LOG_CHANNEL, f"ERROR getting IMDb Detail in Indonesia:\n<code>{str(err)}</code>")


@app.on_callback_query(filters.regex("^imdbres_en"))
@ratelimiter
async def imdb_en_callback(bot, query):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    await query.message.edit_caption("<i>⏳ Getting IMDb source..</i>")
    try:
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await http.get(url, headers=headers)
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(sop.find("script", attrs={"type": "application/ld+json"}).contents[0])
        ott = await search_jw(r_json.get("name"), "US")
        typee = r_json.get("@type", "")
        res_str = ""
        tahun = re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0] if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text) else "N/A"
        res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n"
        if aka := r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
        else:
            res_str += "\n"
        if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = durasi[0].find(class_="ipc-metadata-list-item__content-container").text
            res_str += f"<b>Duration:</b> <code>{durasi}</code>\n"
        if kategori := r_json.get("contentRating"):
            res_str += f"<b>Category:</b> <code>{kategori}</code> \n"
        if rating := r_json.get("aggregateRating"):
            res_str += f"<b>Rating:</b> <code>{rating['ratingValue']}⭐️ from {rating['ratingCount']} users</code>\n"
        if release := sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = release[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
            rilis_url = release[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")["href"]
            res_str += f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
        if genre := r_json.get("genre"):
            genre = "".join(f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, " if i in GENRES_EMOJI else f"#{i.replace('-', '_').replace(' ', '_')}, " for i in r_json["genre"])
            genre = genre[:-2]
            res_str += f"<b>Genre:</b> {genre}\n"
        if negara := sop.select('li[data-testid="title-details-origin"]'):
            country = "".join(f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, " for country in negara[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
            country = country[:-2]
            res_str += f"<b>Country:</b> {country}\n"
        if bahasa := sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(f"#{lang.text.replace(' ', '_').replace('-', '_')}, " for lang in bahasa[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
            language = language[:-2]
            res_str += f"<b>Language:</b> {language}\n"
        res_str += "\n<b>🙎 Cast Info:</b>\n"
        if directors := r_json.get("director"):
            director = ""
            for i in directors:
                name = i["name"]
                url = i["url"]
                director += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            director = director[:-2]
            res_str += f"<b>Director:</b> {director}\n"
        if creators := r_json.get("creator"):
            creator = ""
            for i in creators:
                if i["@type"] == "Person":
                    name = i["name"]
                    url = i["url"]
                    creator += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            creator = creator[:-2]
            res_str += f"<b>Writer:</b> {creator}\n"
        if actor := r_json.get("actor"):
            actors = ""
            for i in actor:
                name = i["name"]
                url = i["url"]
                actors += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            actors = actors[:-2]
            res_str += f"<b>Stars:</b> {actors}\n\n"
        if description := r_json.get("description"):
            res_str += f"<b>📜 Summary: </b> <code>{description}</code>\n\n"
        if keywd := r_json.get("keywords"):
            keywords = keywd.split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_").replace("-", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Keywords:</b> {key_} \n"
        if award := sop.select('li[data-testid="award_information"]'):
            awards = award[0].find(class_="ipc-metadata-list-item__list-content-item").text
            res_str += f"<b>🏆 Awards:</b> <code>{awards}</code>\n"
        else:
            res_str += "\n"
        if ott != "":
            res_str += f"Available On:\n{ott}\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if trailer := r_json.get("trailer"):
            trailer_url = trailer["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}")]])
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(InputMediaPhoto(thumb, caption=res_str, parse_mode=enums.ParseMode.HTML), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(InputMediaPhoto(poster, caption=res_str, parse_mode=enums.ParseMode.HTML), reply_markup=markup)
            except Exception:
                await query.message.edit_caption(res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
    except (MessageNotModified, MessageIdInvalid):
        pass
    except Exception as exc:
        err = traceback.format_exc(limit=20)
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>\n<b>Full Error:</b> <code>{err}</code>\n\nPlease report to owner with detail of error, or your report will be ignored.")
        await app.send_message(LOG_CHANNEL, f"ERROR getting IMDb Detail in Eng:\n<code>{str(err)}</code>")
