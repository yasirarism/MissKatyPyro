import json
import re
import logging
from utils import demoji
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto,
)
from bs4 import BeautifulSoup
from pyrogram import filters
from misskaty import app, BOT_USERNAME
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.tools import GENRES_EMOJI, get_random_string
from misskaty.helper.http import http

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
    buttons = InlineKeyboard(row_width=2)
    ranval = get_random_string(4)
    LIST_CARI[ranval] = m.text.split(None, 1)[1]
    buttons.add(
        InlineButton("🇺🇸 English", f"imdbcari_en#{ranval}#{m.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"imdcari_id#{ranval}#{m.from_user.id}"),
        InlineButton("❌ Close", f"close#{m.from_user.id}"),
    )
    await m.reply_photo(
        "https://telegra.ph/file/270955ef0d1a8a16831a9.jpg",
        caption=
        f"Hi {m.from_user.mention}, Please select the language you want to use on IMDB Search.\n\nSilakan pilih bahasa yang ingin Anda gunakan di Pencarian IMDB.",
        reply_markup=buttons,
        quote=True,
    )


@app.on_callback_query(filters.regex("^imdcari_id"))
async def imdbcari_id(client, query):
    BTN = []
    i, msg, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer(f"⚠️ Akses Ditolak!", True)
    try:
        kueri = LIST_CARI.get(msg)
        del LIST_CARI[msg]
    except KeyError:
        return await query.message.edit_caption(f"⚠️ Callback Query Sudah Expired!", True)
    await query.message.edit_caption("<i>🔎 Sedang mencari di Database IMDB..</i>")
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await http.get(f"https://yasirapi.eu.org/imdb-search?q={kueri}"
                               )
        res = json.loads(r.text).get("result")
        if not res:
            return await query.message.edit_caption(
                f"⛔️ Tidak ditemukan hasil untuk kueri: <code>{kueri}</code>")
        msg += f"🎬 Ditemukan ({len(res)}) hasil dari: <code>{kueri}</code> ~ {query.from_user.mention}\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("l")
            year = f"({movie.get('y')})" if movie.get("y") else ""
            type = movie.get("q").replace("feature", "movie").capitalize()
            movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
            msg += f"{num}. {title} {year} - {type}\n"
            BTN.append(
                InlineKeyboardButton(
                    text=num, callback_data=f"imdbres_id#{uid}#{movieID}"))
        BTN.append(
            InlineKeyboardButton(text="❌ Close", callback_data=f"close#{uid}"))
        buttons.add(*BTN)
        await query.message.edit_caption(msg, reply_markup=buttons)
    except Exception as err:
        await query.message.edit_caption(
            f"Ooppss, gagal mendapatkan daftar judul di IMDb.\n\n<b>ERROR:</b> <code>{err}</code>"
        )


@app.on_callback_query(filters.regex("^imdbcari_en"))
async def imdbcari_en(client, query):
    BTN = []
    i, msg, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer(f"⚠️ Access Denied!", True)
    try:
        kueri = LIST_CARI.get(msg)
        del LIST_CARI[msg]
    except KeyError:
        return await query.message.edit_caption(f"⚠️ Callback Query Expired!", True)
    await query.message.edit_caption("<i>🔎 Looking in the IMDB Database..</i>")
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await http.get(f"https://yasirapi.eu.org/imdb-search?q={kueri}"
                               )
        res = json.loads(r.text).get("result")
        if not res:
            return await query.message.edit_caption(
                f"⛔️ Result not found for keywords: <code>{kueri}</code>")
        msg += f"🎬 Found ({len(res)}) result for keywords: <code>{kueri}</code> ~ {query.from_user.mention}\n\n"
        for num, movie in enumerate(res, start=1):
            title = movie.get("l")
            year = f"({movie.get('y')})" if movie.get("y") else ""
            type = movie.get("q").replace("feature", "movie").capitalize()
            movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
            msg += f"{num}. {title} {year} - {type}\n"
            BTN.append(InlineKeyboardButton(text=num, callback_data=f"imdbres_en#{query.from_user.id}#{movieID}"))
        BTN.append(InlineKeyboardButton(text="❌ Close", callback_data=f"close#{query.from_user.id}"))
        buttons.add(*BTN)
        await query.message.edit_caption(msg, reply_markup=buttons)
    except Exception as err:
        await query.message.edit_caption(
            f"Failed when requesting movies title @ IMDb\n\n<b>ERROR:</b> <code>{err}</code>"
        )


@app.on_callback_query(filters.regex("^imdbres_id"))
async def imdb_id_callback(bot, query):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    try:
        await query.message.edit_caption("⏳ Permintaan kamu sedang diproses.. "
                                         )
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await http.get(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"
            },
        )
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(
            sop.find("script", attrs={
                "type": "application/ld+json"
            }).contents[0])
        res_str = ""
        type = f"<code>{r_json['@type']}</code>" if r_json.get("@type") else ""
        if r_json.get("name"):
            try:
                tahun = (sop.select(
                    'ul[data-testid="hero-title-block__metadata"]')[0].find(
                        class_="sc-8c396aa2-2 itZqyK").text)
            except:
                tahun = "-"
            res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json['name']} [{tahun}]</a> (<code>{type}</code>)\n"
        if r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
        else:
            res_str += "\n"
        if sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = (
                sop.select('li[data-testid="title-techspec_runtime"]')[0].find(
                    class_="ipc-metadata-list-item__content-container").text)
            res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>Kategori:</b> <code>{r_json['contentRating']}</code> \n"
        if r_json.get("aggregateRating"):
            res_str += f"<b>Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
        if sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = (sop.select(
                'li[data-testid="title-details-releasedate"]'
            )[0].find(
                class_=
                "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
            ).text)
            rilis_url = sop.select(
                'li[data-testid="title-details-releasedate"]'
            )[0].find(
                class_=
                "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
            )["href"]
            res_str += (
                f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
            )
        if r_json.get("genre"):
            genre = ""
            for i in r_json["genre"]:
                if i in GENRES_EMOJI:
                    genre += (
                        f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                    )
                else:
                    genre += f"#{i.replace('-', '_').replace(' ', '_')}, "
            genre = genre[:-2]
            res_str += f"<b>Genre:</b> {genre}\n"
        if sop.select('li[data-testid="title-details-origin"]'):
            country = "".join(
                f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, "
                for country in sop.
                select('li[data-testid="title-details-origin"]')[0].findAll(
                    class_=
                    "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                ))
            country = country[:-2]
            res_str += f"<b>Negara:</b> {country}\n"
        if sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(
                f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                for lang in sop.
                select('li[data-testid="title-details-languages"]')[0].findAll(
                    class_=
                    "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                ))
            language = language[:-2]
            res_str += f"<b>Bahasa:</b> {language}\n"
        res_str += "\n<b>🙎 Info Cast:</b>\n"
        if r_json.get("director"):
            director = ""
            for i in r_json["director"]:
                name = i["name"]
                url = i["url"]
                director += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            director = director[:-2]
            res_str += f"<b>Sutradara:</b> {director}\n"
        if r_json.get("creator"):
            creator = ""
            for i in r_json["creator"]:
                if i["@type"] == "Person":
                    name = i["name"]
                    url = i["url"]
                    creator += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            creator = creator[:-2]
            res_str += f"<b>Penulis:</b> {creator}\n"
        if r_json.get("actor"):
            actors = ""
            for i in r_json["actor"]:
                name = i["name"]
                url = i["url"]
                actors += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            actors = actors[:-2]
            res_str += f"<b>Pemeran:</b> {actors}\n\n"
        if r_json.get("description"):
            summary = GoogleTranslator("auto", "id").translate(
                r_json.get("description"))
            res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
        if r_json.get("keywords"):
            keywords = r_json["keywords"].split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_").replace("-", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Kata Kunci:</b> {key_} \n"
        if sop.select('li[data-testid="award_information"]'):
            awards = (
                sop.select('li[data-testid="award_information"]')[0].find(
                    class_="ipc-metadata-list-item__list-content-item").text)
            res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(awards)}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if r_json.get("trailer"):
            trailer_url = r_json["trailer"]["url"]
            markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"),
                InlineKeyboardButton("▶️ Trailer", url=trailer_url),
            ]])
        else:
            markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}")
            ]])
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(InputMediaPhoto(
                    thumb, caption=res_str),
                                               reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(InputMediaPhoto(
                    poster, caption=res_str),
                                               reply_markup=markup)
            except Exception:
                await query.message.edit_caption(res_str, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, reply_markup=markup)
    except MessageNotModified:
        pass
    except Exception:
        exc = traceback.format_exc()
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
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"
            },
        )
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(sop.find("script", attrs={"type": "application/ld+json"}).contents[0])
        res_str = ""
        type = f"<code>{r_json['@type']}</code>" if r_json.get("@type") else ""
        if r_json.get("name"):
            try:
                tahun = sop.select('ul[data-testid="hero-title-block__metadata"]')[0].find(class_="sc-8c396aa2-2 itZqyK").text
            except:
                tahun = "-"
            res_str += f"<b>📹 Title:</b> <a href='{url}'>{r_json['name']} [{tahun}]</a> (<code>{type}</code>)\n"
        if r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
        else:
            res_str += "\n"
        if sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = sop.select('li[data-testid="title-techspec_runtime"]')[0].find(class_="ipc-metadata-list-item__content-container").text
            res_str += f"<b>Duration:</b> <code>{durasi}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>Category:</b> <code>{r_json['contentRating']}</code> \n"
        if r_json.get("aggregateRating"):
            res_str += f"<b>Rating:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ from {r_json['aggregateRating']['ratingCount']} user</code> \n"
        if sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = sop.select('li[data-testid="title-details-releasedate"]')[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
            rilis_url = sop.select('li[data-testid="title-details-releasedate"]')[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")["href"]
            res_str += f"<b>Release Data:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
        if r_json.get("genre"):
            genre = ""
            for i in r_json["genre"]:
                if i in GENRES_EMOJI:
                    genre += f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                else:
                    genre += f"#{i.replace('-', '_').replace(' ', '_')}, "
            genre = genre[:-2]
            res_str += f"<b>Genre:</b> {genre}\n"
        if sop.select('li[data-testid="title-details-origin"]'):
            country = "".join(
                f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, "
                for country in sop.select('li[data-testid="title-details-origin"]')[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
            )
            country = country[:-2]
            res_str += f"<b>Country:</b> {country}\n"
        if sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(
                f"#{lang.text.replace(' ', '_').replace('-', '_')}, " for lang in sop.select('li[data-testid="title-details-languages"]')[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
            )
            language = language[:-2]
            res_str += f"<b>Language:</b> {language}\n"
        res_str += "\n<b>🙎 Cast Info:</b>\n"
        if r_json.get("director"):
            director = ""
            for i in r_json["director"]:
                name = i["name"]
                url = i["url"]
                director += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            director = director[:-2]
            res_str += f"<b>Director:</b> {director}\n"
        if r_json.get("creator"):
            creator = ""
            for i in r_json["creator"]:
                if i["@type"] == "Person":
                    name = i["name"]
                    url = i["url"]
                    creator += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            creator = creator[:-2]
            res_str += f"<b>Penulis:</b> {creator}\n"
        if r_json.get("actor"):
            actors = ""
            for i in r_json["actor"]:
                name = i["name"]
                url = i["url"]
                actors += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
            actors = actors[:-2]
            res_str += f"<b>Stars:</b> {actors}\n\n"
        if r_json.get("description"):
            res_str += f"<b>📜 Summary: </b> <code>{r_json['description'].replace('  ', ' ')}</code>\n\n"
        if r_json.get("keywords"):
            keywords = r_json["keywords"].split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_").replace("-", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Keywords:</b> {key_} \n"
        if sop.select('li[data-testid="award_information"]'):
            awards = sop.select('li[data-testid="award_information"]')[0].find(class_="ipc-metadata-list-item__list-content-item").text
            res_str += f"<b>🏆 Awards:</b> <code>{awards}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if r_json.get("trailer"):
            trailer_url = r_json["trailer"]["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
            ]])
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}")]])
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(InputMediaPhoto(thumb, caption=res_str), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(InputMediaPhoto(poster, caption=res_str), reply_markup=markup)
            except Exception:
                await query.message.edit_caption(res_str, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, reply_markup=markup)
    except Exception:
        exc = traceback.format_exc()
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")
