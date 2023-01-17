import json
import logging
import re

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import filters
from pyrogram.errors import (
    MediaEmpty,
    MessageNotModified,
    PhotoInvalidDimensions,
    WebpageMediaEmpty,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from database.imdb_db import *
from misskaty import BOT_USERNAME, app
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from misskaty.helper.tools import get_random_string, search_jw
from misskaty.vars import COMMAND_HANDLER

LOGGER = logging.getLogger(__name__)
LIST_CARI = {}


# IMDB Choose Language
@app.on_message(filters.command(["imdb"], COMMAND_HANDLER))
@capture_err
async def imdb_choose(_, m):
    if len(m.command) == 1:
        return await m.reply(
            f"ℹ️ Please add query after CMD!\nEx: <code>/{m.command[0]} Jurassic World</code>",
            quote=True,
        )
    if m.sender_chat:
        return await m.reply("This feature not supported for channel..")
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
        InlineButton("🇺🇸 English", f"imdbcari_en#{ranval}#{m.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"imdcari_id#{ranval}#{m.from_user.id}"),
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
        # https://yasirapi.eu.org/imdb-search?q=doraemon # Second API
        r = await http.get(f"https://imdb.yasirapi.eu.org/search?query={kueri}")
        res = r.json().get("results")
        if not res:
            return await k.edit_caption(f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>")
        msg += f"🎬 Ditemukan ({len(res)}) hasil untuk kueri: <code>{kueri}</code>\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("title")
            year = f"({movie.get('year', 'N/A')})"
            typee = movie.get("type", 'N/A').capitalize()
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
        await k.edit_caption(f"Ooppss, gagal mendapatkan daftar judul di IMDb.\n\n<b>ERROR:</b> <code>{err}</code>")


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
        r = await http.get(f"https://imdb.yasirapi.eu.org/search?query={kueri}")
        res = r.json().get("results")
        if not res:
            return await k.edit_caption(f"⛔️ Result not found for keywords: <code>{kueri}</code>")
        msg += f"🎬 Found ({len(res)}) result for keywords: <code>{kueri}</code>\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("title")
            year = f"({movie.get('year', 'N/A')})"
            typee = movie.get("type", "N/A").capitalize()
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
        await k.edit_caption(f"Failed when requesting movies title.\n\n<b>ERROR:</b> <code>{err}</code>")


@app.on_callback_query(filters.regex("^imdcari_id"))
async def imdbcari_id(client, query):
    BTN = []
    i, msg, uid = query.data.split("#")
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
        r = await http.get(f"https://imdb.yasirapi.eu.org/search?query={kueri}")
        res = r.json().get("results")
        if not res:
            return await query.message.edit_caption(f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>")
        msg += f"🎬 Ditemukan ({len(res)}) hasil dari: <code>{kueri}</code> ~ {query.from_user.mention}\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("title")
            year = f"({movie.get('year', 'N/A')})"
            typee = movie.get("type", "N/A").capitalize()
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
        await query.message.edit_caption(f"Ooppss, gagal mendapatkan daftar judul di IMDb.\n\n<b>ERROR:</b> <code>{err}</code>")


@app.on_callback_query(filters.regex("^imdbcari_en"))
async def imdbcari_en(client, query):
    BTN = []
    i, msg, uid = query.data.split("#")
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
        r = await http.get(f"https://imdb.yasirapi.eu.org/search?query={kueri}")
        res = r.json().get("results")
        if not res:
            return await query.message.edit_caption(f"⛔️ Result not found for keywords: <code>{kueri}</code>")
        msg += f"🎬 Found ({len(res)}) result for keywords: <code>{kueri}</code> ~ {query.from_user.mention}\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("title")
            year = f"({movie.get('year', 'N/A')})"
            typee = movie.get("type", "N/A").capitalize()
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
        await query.message.edit_caption(f"Failed when requesting movies title @ IMDb\n\n<b>ERROR:</b> <code>{err}</code>")


@app.on_callback_query(filters.regex("^imdbres_id"))
async def imdb_id_callback(_, query):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    try:
        await query.message.edit_caption("⏳ Permintaan kamu sedang diproses.. ")
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await http.get(
            f"https://yasirapi.eu.org/imdb-page?url={url}",
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"},
        )
        r_json = resp.json().get("result")
        ott = await search_jw(r_json.get("title"), "en_ID")
        res_str = ""
        if judul := r_json.get("title"):
            res_str += f"<b>📹 Judul:</b> <a href='{url}'>{judul} [{r_json.get('year')}]</a>\n"
        if aka := r_json.get("aka"):
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
        else:
            res_str += "\n"
        if durasi := r_json.get("duration"):
            res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
        if kategori := r_json.get("category"):
            res_str += f"<b>Kategori:</b> <code>{kategori}</code> \n"
        if rating := r_json.get("rating"):
            res_str += f"<b>Peringkat:</b> <code>{GoogleTranslator('auto', 'id').translate(rating)}</code>\n"
        if release := r_json.get("release_date"):
            res_str += f"<b>Rilis:</b> {release}\n"
        if genre := r_json.get("genre"):
            res_str += f"<b>Genre :</b> {genre}\n"
        if negara := r_json.get("country"):
            res_str += f"<b>Negara:</b> {negara}\n"
        if bahasa := r_json.get("language"):
            res_str += f"<b>Bahasa:</b> {bahasa}\n"
        res_str += "\n<b>🙎 Info Cast:</b>\n"
        if director := r_json.get("director"):
            res_str += f"<b>Sutradara:</b> {director}\n"
        if creator := r_json.get("creator"):
            res_str += f"<b>Penulis:</b> {creator}\n"
        if actors := r_json.get("actors"):
            res_str += f"<b>Pemeran:</b> {actors}\n\n"
        if deskripsi := r_json.get("description"):
            summary = GoogleTranslator("auto", "id").translate(deskripsi)
            res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
        if key_ := r_json.get("keyword"):
            res_str += f"<b>🔥 Kata Kunci:</b> {key_} \n"
        if award := r_json.get("awards"):
            res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(award)}</code>\n\n"
        else:
            res_str += "\n"
        if ott != "":
            res_str += f"Tersedia di:\n{ott}\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if trailer := r_json.get("trailer_url"):
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=url),
                        InlineKeyboardButton("▶️ Trailer", url=trailer),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=url)]])
        if thumb := r_json.get("thumb"):
            try:
                await query.message.edit_media(InputMediaPhoto(thumb, caption=res_str), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(InputMediaPhoto(poster, caption=res_str), reply_markup=markup)
            except Exception:
                await query.message.edit_caption(res_str, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, reply_markup=markup)
    except MessageNotModified:
        pass
    except Exception as exc:
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")


@app.on_callback_query(filters.regex("^imdbres_en"))
async def imdb_en_callback(bot, query):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    await query.message.edit_caption("<i>⏳ Getting IMDb source..</i>")
    try:
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await http.get(
            f"https://yasirapi.eu.org/imdb-page?url={url}",
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"},
        )
        r_json = resp.json().get("result")
        ott = await search_jw(r_json.get("title"), "en_US")
        res_str = ""
        if judul := r_json.get("title"):
            res_str += f"<b>📹 Title:</b> <a href='{url}'>{judul} [{r_json.get('year')}]</a>\n"
        if aka := r_json.get("aka"):
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
        else:
            res_str += "\n"
        if durasi := r_json.get("duration"):
            res_str += f"<b>Duration:</b> <code>{durasi}</code>\n"
        if kategori := r_json.get("category"):
            res_str += f"<b>Category:</b> <code>{kategori}</code> \n"
        if rating := r_json.get("rating"):
            res_str += f"<b>Rating:</b> <code>{rating}\n"
        if release := r_json.get("release_date"):
            res_str += f"<b>Release Data:</b> {release}\n"
        if genre := r_json.get("genre"):
            res_str += f"<b>Genre:</b> {genre}\n"
        if country := r_json.get("country"):
            res_str += f"<b>Country:</b> {country}\n"
        if language := r_json.get("language"):
            res_str += f"<b>Language:</b> {language}\n"
        res_str += "\n<b>🙎 Cast Info:</b>\n"
        if director := r_json.get("director"):
            res_str += f"<b>Director:</b> {director}\n"
        if writer := r_json.get("creator"):
            res_str += f"<b>Writer:</b> {writer}\n"
        if actors := r_json.get("actors"):
            res_str += f"<b>Stars:</b> {actors}\n\n"
        if description := r_json.get("description"):
            res_str += f"<b>📜 Summary: </b> <code>{description}</code>\n\n"
        if key_ := r_json.get("keyword"):
            res_str += f"<b>🔥 Keywords:</b> {key_} \n"
        if award := r_json.get("awards"):
            res_str += f"<b>🏆 Awards:</b> <code>{award}</code>\n\n"
        else:
            res_str += "\n"
        if ott != "":
            res_str += f"Available On:\n{ott}\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if trailer := r_json.get("trailer_url"):
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=url),
                        InlineKeyboardButton("▶️ Trailer", url=trailer),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=url)]])
        if thumb := r_json.get("thumb"):
            try:
                await query.message.edit_media(InputMediaPhoto(thumb, caption=res_str), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(InputMediaPhoto(poster, caption=res_str), reply_markup=markup)
            except Exception:
                await query.message.edit_caption(res_str, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, reply_markup=markup)
    except Exception as exc:
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")
