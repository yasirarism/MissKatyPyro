# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import contextlib
import html
import json
import logging
import re
import sys
from urllib.parse import quote_plus

import emoji
import httpx
from bs4 import BeautifulSoup
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import Client, enums
from pyrogram.errors import (
    ListenerTimeout,
    MediaCaptionTooLong,
    MediaEmpty,
    MessageIdInvalid,
    MessageNotModified,
    PhotoInvalidDimensions,
    RPCError,
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

from database.imdb_db import (
    add_imdbset,
    clear_imdb_template,
    get_imdb_template,
    is_imdbset,
    remove_imdbset,
    set_imdb_template,
)
from misskaty import app
from misskaty.helper import GENRES_EMOJI, Cache, fetch, gtranslate, get_random_string, search_jw
from utils import demoji

LOGGER = logging.getLogger("MissKaty")
LIST_CARI = Cache(filename="imdb_cache.db", path="cache", in_memory=False)
SUPPORTED_TEMPLATE_TAGS = (
    "#TITLE {title} #TYPE {type} #DURATION {duration} #CATEGORY {category} "
    "#RATING {rating} #USER_RATING {user_rating} #RELEASE_DATE {release_date} "
    "#GENRE {genre} #COUNTRY {country} #LANGUAGE {language} #CAST_INFO {cast_info} "
    "#SINOPSIS {sinopsis} #KEYWORD {keyword} #AWARDS {awards} #OTT {ott}"
)


def _format_number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return "N/A"


def _parse_duration(duration_iso, fallback_text=None):
    hours = minutes = seconds = 0
    if duration_iso:
        if match := re.search(r"(?P<hour>\d+)H", duration_iso):
            hours = int(match.group("hour"))
        if match := re.search(r"(?P<minute>\d+)M", duration_iso):
            minutes = int(match.group("minute"))
        if match := re.search(r"(?P<second>\d+)S", duration_iso):
            seconds = int(match.group("second"))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    total_minutes = (total_seconds // 60) if total_seconds else 0
    if hours or minutes:
        duration_text = f"{hours}h {minutes}m".strip()
    elif seconds:
        duration_text = f"{seconds}s"
    else:
        duration_text = fallback_text or "N/A"
    return duration_text, str(total_seconds or ""), str(total_minutes or ""), fallback_text or duration_text


def _format_country_name(raw_text: str):
    country_text = emoji.replace_emoji(raw_text or "", replace="").strip()
    country_text = country_text or raw_text.strip()
    flag = demoji(country_text) if country_text else ""
    if flag.startswith(":") and flag.endswith(":"):
        flag = ""
    display = f"{flag} {country_text}".strip() if country_text else "N/A"
    return country_text, display


def _build_cast_summary(language: str, directors: str, writers: str, actors: str) -> str:
    parts = []
    if language == "id":
        if directors:
            parts.append(f"<b>Sutradara:</b> {directors}")
        if writers:
            parts.append(f"<b>Penulis:</b> {writers}")
        if actors:
            parts.append(f"<b>Pemeran:</b> {actors}")
    else:
        if directors:
            parts.append(f"<b>Director:</b> {directors}")
        if writers:
            parts.append(f"<b>Writer:</b> {writers}")
        if actors:
            parts.append(f"<b>Stars:</b> {actors}")
    return "\n".join(parts) or "N/A"


def _apply_template(template: str, data: dict) -> str:
    result = template
    for placeholder, value in data.items():
        result = result.replace(placeholder, value)
    return result


def _build_default_caption(language: str, data: dict) -> str:
    if language == "id":
        lines = [
            f"<b>📹 Judul:</b> {data['title']} [{data['year']}]",
            f"<b>Tipe:</b> {data['type']}",
            f"<b>Durasi:</b> {data['runtime']}",
            f"<b>Kategori:</b> {data['content_rating']}",
            f"<b>Rating:</b> {data['rating']}⭐️",
            f"<b>Penilaian Pengguna:</b> {data['votes']}",
            f"<b>Tanggal Rilis:</b> {data['release']}",
            f"<b>Genre:</b> {data['genres']}",
            f"<b>Negara:</b> {data['countries']}",
            f"<b>Bahasa:</b> {data['languages']}",
            "",
            f"<b>🙎 Info Cast:</b>\n{data['cast_info']}",
            "",
            "<b>📜 Sinopsis:</b>",
            data["plot"],
        ]
        if data["keywords"]:
            lines.extend(["", "<b>🔥 Kata Kunci:</b>", data["keywords"]])
        if data["awards"]:
            lines.extend(["<b>🏆 Penghargaan:</b>", data["awards"]])
        if data["ott"]:
            lines.extend(["<b>Tersedia di:</b>", data["ott"]])
        lines.append(f"<b>©️ IMDb by</b> @{data['bot_username']}")
        return "\n".join(lines)
    else:
        lines = [
            f"<b>📹 Title:</b> {data['title']} [{data['year']}]",
            f"<b>Type:</b> {data['type']}",
            f"<b>Duration:</b> {data['runtime']}",
            f"<b>Category:</b> {data['content_rating']}",
            f"<b>Rating:</b> {data['rating']}⭐️",
            f"<b>User Rating:</b> {data['votes']}",
            f"<b>Release Date:</b> {data['release']}",
            f"<b>Genre:</b> {data['genres']}",
            f"<b>Country:</b> {data['countries']}",
            f"<b>Language:</b> {data['languages']}",
            "",
            f"<b>🙎 Cast Info:</b>\n{data['cast_info']}",
            "",
            "<b>📜 Synopsis:</b>",
            data["plot"],
        ]
        if data["keywords"]:
            lines.extend(["", "<b>🔥 Keywords:</b>", data["keywords"]])
        if data["awards"]:
            lines.extend(["<b>🏆 Awards:</b>", data["awards"]])
        if data["ott"]:
            lines.extend(["<b>Available On:</b>", data["ott"]])
        lines.append(f"<b>©️ IMDb by</b> @{data['bot_username']}")
        return "\n".join(lines)


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
    LIST_CARI.add(ranval, kuery, timeout=15)
    buttons.row(
        InlineButton("🇺🇸 English", f"imdbcari#eng#{ranval}#{ctx.from_user.id}"),
        InlineButton("🇮🇩 Indonesia", f"imdbcari#ind#{ranval}#{ctx.from_user.id}"),
    )
    buttons.row(InlineButton("🚩 Set Default Language", f"imdbset#{ctx.from_user.id}"))
    buttons.row(InlineButton("❌ Close", f"close#{ctx.from_user.id}"))
    await ctx.reply_photo(
        "https://img.yasirweb.eu.org/file/270955ef0d1a8a16831a9.jpg",
        caption=f"Hi {ctx.from_user.mention}, Please select the language you want to use on IMDB Search. If you want use default lang for every user, click third button. So no need click select lang if use CMD.\n\nTimeout: 10s",
        reply_markup=buttons,
        quote=True,
    )


@app.on_cmd("set_custom_template")
async def set_imdb_custom_template(_, message: Message):
    if message.sender_chat:
        return await message.reply_msg(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    if len(message.command) == 1:
        current = await get_imdb_template(message.from_user.id)
        info_text = (
            "you can now set custom template for @IMDbOT posts!\n"
            "Usage:\n"
            "<code>/set_custom_template &lt;b&gt;#TITLE&lt;/b&gt; | #TYPE</code>\n"
            "<code>&lt;i&gt;#DURATION&lt;/i&gt; ⭐️&lt;b&gt;#RATING&lt;/b&gt; | #USER_RATING</code>\n\n"
            "Send <code>/set_custom_template reset</code> to remove your custom template.\n\n"
            f"Supported Tags:\n{SUPPORTED_TEMPLATE_TAGS}"
        )
        if current:
            info_text += f"\n\nCurrent Template:\n<code>{current}</code>"
        return await message.reply_msg(info_text, quote=True)
    template = message.text.split(None, 1)[1]
    if template.lower() in ("reset", "clear", "default", "remove", "off"):
        await clear_imdb_template(message.from_user.id)
        return await message.reply_msg(
            "Custom IMDb template has been cleared.", quote=True, del_in=7
        )
    await set_imdb_template(message.from_user.id, template)
    await message.reply_msg(
        "Custom IMDb template saved successfully!\n"
        "Use the supported tags above to personalize your posts.",
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
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit_caption(
            "<i>Please select available language below..</i>", reply_markup=buttons
        )


@app.on_cb("setimdb")
async def imdbsetlang(_, query: CallbackQuery):
    _, lang, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    _, langset = await is_imdbset(query.from_user.id)
    if langset == lang:
        return await query.answer(f"⚠️ Your Setting Already in ({langset})!", True)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
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


async def imdb_search_id(kueri, message):
    BTN = []
    k = await message.reply_photo(
        "https://img.yasirweb.eu.org/file/270955ef0d1a8a16831a9.jpg",
        caption=f"🔎 Menelusuri <code>{kueri}</code> di database IMDb ...",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    with contextlib.redirect_stdout(sys.stderr):
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
            msg += (
                f"🎬 Ditemukan ({len(res)}) hasil untuk kueri: <code>{kueri}</code>\n\n"
            )
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
            await k.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>")
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
    with contextlib.redirect_stdout(sys.stderr):
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
            msg += (
                f"🎬 Found ({len(res)}) result for keywords: <code>{kueri}</code>\n\n"
            )
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
            await k.edit_caption(f"HTTP Exception for IMDB Search - <code>{exc}</code>")
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
        with contextlib.suppress(MessageIdInvalid, MessageNotModified):
            await query.message.edit_caption(
                "<i>🔎 Sedang mencari di Database IMDB..</i>"
            )
        msg = ""
        buttons = InlineKeyboard(row_width=4)
        with contextlib.redirect_stdout(sys.stderr):
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
                        InlineKeyboardButton(
                            text="❌ Close", callback_data=f"close#{uid}"
                        ),
                    )
                )
                buttons.add(*BTN)
                await query.message.edit_caption(msg, reply_markup=buttons)
            except httpx.HTTPError as exc:
                await query.message.edit_caption(
                    f"HTTP Exception for IMDB Search - <code>{exc}</code>"
                )
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
        with contextlib.redirect_stdout(sys.stderr):
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
                        InlineKeyboardButton(
                            text="❌ Close", callback_data=f"close#{uid}"
                        ),
                    )
                )
                buttons.add(*BTN)
                await query.message.edit_caption(msg, reply_markup=buttons)
            except httpx.HTTPError as exc:
                await query.message.edit_caption(
                    f"HTTP Exception for IMDB Search - <code>{exc}</code>"
                )
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
    with contextlib.redirect_stdout(sys.stderr):
        try:
            await query.message.edit_caption("⏳ Permintaan kamu sedang diproses.. ")
            imdb_id = f"tt{movie}"
            imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
            resp = await fetch.get(imdb_url)
            resp.raise_for_status()
            sop = BeautifulSoup(resp, "lxml")
            r_json = json.loads(
                sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
            )
            title = r_json.get("name", "N/A")
            aka = r_json.get("alternateName", "") or "N/A"
            ott = await search_jw(
                r_json.get("alternateName") or r_json.get("name"), "ID"
            )
            typee = r_json.get("@type", "")
            res_str = ""
            tahun = (
                r_json.get("datePublished", "").split("-")[0]
                if r_json.get("datePublished")
                else (
                    re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0]
                    if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)
                    else "N/A"
                )
            )
            rating_info = r_json.get("aggregateRating") or {}
            rating_value = str(rating_info.get("ratingValue", "N/A"))
            rating_count = rating_info.get("ratingCount")
            votes_text = _format_number(rating_count) if rating_count else "N/A"
            content_rating = r_json.get("contentRating", "N/A")
            duration_iso = r_json.get("duration")
            duration_text_raw = ""
            if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
                duration_text_raw = (
                    durasi[0]
                    .find(class_="ipc-metadata-list-item__content-container")
                    .text
                )
            translated_duration = (
                (await gtranslate(duration_text_raw, "auto", "id")).text
                if duration_text_raw
                else ""
            )
            duration_text, duration_seconds, duration_minutes, runtime_display = _parse_duration(
                duration_iso, translated_duration
            )
            rilis = ""
            rilis_url = ""
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
            genres_plain_list = r_json.get("genre") or []
            genres_plain = ", ".join(genres_plain_list) if genres_plain_list else "N/A"
            genres_hash = (
                "".join(
                    f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                    if i in GENRES_EMOJI
                    else f"#{i.replace('-', '_').replace(' ', '_')}, "
                    for i in genres_plain_list
                )[:-2]
                if genres_plain_list
                else ""
            )
            country_plain = "N/A"
            country_hash = ""
            if negara := sop.select('li[data-testid="title-details-origin"]'):
                countries_text = []
                countries_display = []
                for country in negara[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                ):
                    clean_country, display_country = _format_country_name(country.text)
                    if clean_country:
                        countries_text.append(clean_country)
                    if display_country:
                        countries_display.append(display_country)
                country_plain = ", ".join(countries_display) if countries_display else "N/A"
                country_hash = (
                    ", ".join(
                        f"#{country.replace(' ', '_').replace('-', '_')}" for country in countries_text
                    )
                    if countries_text
                    else ""
                )
            language_plain = "N/A"
            language_hash = ""
            if bahasa := sop.select('li[data-testid="title-details-languages"]'):
                languages = [
                    lang.text
                    for lang in bahasa[0].findAll(
                        class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                    )
                ]
                language_plain = ", ".join(languages)
                language_hash = ", ".join(
                    f"#{lang.replace(' ', '_').replace('-', '_')}" for lang in languages
                )
            director_links = ""
            director_names = ""
            if directors := r_json.get("director"):
                director_links = ", ".join(
                    f"<a href='{i['url']}'>{i['name']}</a>" for i in directors
                )
                director_names = ", ".join(i["name"] for i in directors)
            writer_links = ""
            writer_names = ""
            if creators := r_json.get("creator"):
                writer_links = ", ".join(
                    f"<a href='{i['url']}'>{i['name']}</a>"
                    for i in creators
                    if i["@type"] == "Person"
                )
                writer_names = ", ".join(
                    i["name"] for i in creators if i["@type"] == "Person"
                )
            actor_links = ""
            actor_names = ""
            if actors := r_json.get("actor"):
                actor_links = ", ".join(
                    f"<a href='{i['url']}'>{i['name']}</a>" for i in actors
                )
                actor_names = ", ".join(i["name"] for i in actors)
            summary = ""
            short_desc = ""
            if deskripsi := r_json.get("description"):
                summary = (await gtranslate(deskripsi, "auto", "id")).text
                short_desc = summary[:217] + "..." if len(summary) > 220 else summary
            awards_text = ""
            if award := sop.select('li[data-testid="award_information"]'):
                awards = (
                    award[0]
                    .find(class_="ipc-metadata-list-item__list-content-item")
                    .text
                )
                awards_text = (await gtranslate(awards, "auto", "id")).text
            keywords_block = ""
            keywords_plain_text = ""
            if keywd := r_json.get("keywords"):
                keywords_list = [i.strip() for i in keywd.split(",") if i.strip()]
                keywords_block = (
                    "".join(
                        f"#{i.replace(' ', '_').replace('-', '_')}, "
                        for i in keywords_list
                    )[:-2]
                    if keywords_list
                    else ""
                )
                keywords_plain_text = ", ".join(keywords_list)
            trailer_url = r_json.get("trailer", {}).get("url", "")
            poster = r_json.get("image", "")
            cast_summary = _build_cast_summary(
                "id", html.escape(director_names or ""), html.escape(writer_names or ""), html.escape(actor_names or "")
            )
            default_caption_data = {
                "title": html.escape(title),
                "year": html.escape(tahun),
                "type": html.escape(typee),
                "runtime": html.escape(runtime_display),
                "content_rating": html.escape(content_rating or "N/A"),
                "rating": html.escape(rating_value),
                "votes": html.escape(votes_text),
                "release": html.escape(rilis or "N/A"),
                "genres": html.escape(genres_plain or "N/A"),
                "countries": html.escape(country_plain or "N/A"),
                "languages": html.escape(language_plain or "N/A"),
                "cast_info": cast_summary,
                "plot": html.escape(summary or "N/A"),
                "keywords": html.escape(keywords_plain_text or ""),
                "awards": html.escape(awards_text or ""),
                "ott": ott or "",
                "bot_username": html.escape(self.me.username),
            }
            cast_info_block = "\n<b>🙎 Info Cast:</b>\n"
            if director_links:
                cast_info_block += f"<b>Sutradara:</b> {director_links}\n"
            if writer_links:
                cast_info_block += f"<b>Penulis:</b> {writer_links}\n"
            if actor_links:
                cast_info_block += f"<b>Pemeran:</b> {actor_links}\n"
            if cast_info_block.strip() == "<b>🙎 Info Cast:</b>":
                cast_info_block += "N/A\n"
            plot_block = ""
            if summary:
                plot_block = f"<b>📜 Plot:</b>\n<blockquote><code>{summary}</code></blockquote>\n\n"
            res_str += f"<b>📹 Judul:</b> <a href='{imdb_url}'>{title} [{tahun}]</a> (<code>{typee}</code>)\n"
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
            res_str += f"<b>Durasi:</b> <code>{runtime_display}</code>\n"
            if content_rating:
                res_str += f"<b>Kategori:</b> <code>{content_rating}</code> \n"
            if rating_info:
                res_str += f"<b>Peringkat:</b> <code>{rating_value}⭐️ dari {votes_text} pengguna</code>\n"
            if rilis:
                res_str += f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
            if genres_hash:
                res_str += f"<b>Genre:</b> {genres_hash}\n"
            if country_hash:
                res_str += f"<b>Negara:</b> {country_hash}\n"
            if language_hash:
                res_str += f"<b>Bahasa:</b> {language_hash}\n"
            res_str += cast_info_block
            if plot_block:
                res_str += plot_block
            if keywords_block:
                res_str += (
                    f"<b>🔥 Kata Kunci:</b>\n<blockquote>{keywords_block}</blockquote>\n"
                )
            if awards_text:
                res_str += (
                    f"<b>🏆 Penghargaan:</b>\n<blockquote><code>{awards_text}</code></blockquote>\n"
                )
            else:
                res_str += "\n"
            if ott != "":
                res_str += f"Tersedia di:\n{ott}\n"
            res_str += f"<b>©️ IMDb by</b> @{self.me.username}"
            template_text = await get_imdb_template(query.from_user.id)
            template_data = {
                "#AKA": aka,
                "{aka}": aka,
                "#TITLE": title,
                "{title}": title,
                "#TYPE": typee,
                "{type}": typee,
                "#YEAR": tahun,
                "{year}": tahun,
                "#RATING": rating_value,
                "{rating}": rating_value,
                "#USER_RATING": votes_text,
                "{user_rating}": votes_text,
                "#EUSERRATINGS": f"{votes_text} IMDb users",
                "#NUMUSERRATINGS": votes_text,
                "#ONLYRATING": rating_value,
                "#VOTES": votes_text,
                "{votes}": votes_text,
                "#MARINTG": content_rating or "N/A",
                "#DURATION": runtime_display,
                "{duration}": runtime_display,
                "#DURATION_IN_SECONDS": duration_seconds,
                "#DURATION_IN_MINUTES": duration_minutes,
                "{runtime}": runtime_display,
                "#RELEASE_INFO": f"<a href='https://www.imdb.com{rilis_url}'>{rilis}</a>"
                if rilis
                else "N/A",
                "#RELEASE_DATE": rilis or "N/A",
                "{release_date}": rilis or "N/A",
                "#GENRE": genres_hash or genres_plain,
                "{genres}": genres_plain,
                "{genre}": genres_plain,
                "#IMDB_URL": imdb_url,
                "{url}": imdb_url,
                "#IMDB_ID": imdb_id,
                "{imdb_id}": imdb_id,
                "#IMDB_IV": f"<a href='{poster}'>&#8205;</a>" if poster else "",
                "#LANGUAGE": language_plain,
                "#COUNTRY_OF_ORIGIN": country_plain,
                "#LANG": language_plain,
                "#COUNTRY": country_plain,
                "{languages}": language_plain,
                "{language}": language_plain,
                "{countries}": country_plain,
                "{country}": country_plain,
                "#STORY_LINE": summary or "N/A",
                "{plot}": summary or "N/A",
                "{sinopsis}": summary or "N/A",
                "#IMDb_TITLE_TYPE": typee,
                "{kind}": typee,
                "#CATEGORY": content_rating or "N/A",
                "{category}": content_rating or "N/A",
                "#IMDb_SHORT_DESC": short_desc or summary or "N/A",
                "#READ_MORE": f"<a href='{imdb_url}'>Read more</a>",
                "#IMG_HIDDEN_IMG": f"<a href='{poster}'>&#8205;</a>" if poster else "",
                "#IMG_POSTER": poster or "",
                "{poster}": poster or "",
                "#TRAILER": trailer_url,
                "#CAST_INFO_": cast_info_block.strip(),
                "#DIRECTORS_": f"<b>Sutradara:</b> {director_links}" if director_links else "",
                "#WRITERS_": f"<b>Penulis:</b> {writer_links}" if writer_links else "",
                "#ACTORS_": f"<b>Pemeran:</b> {actor_links}" if actor_links else "",
                "#CAST_INFO": cast_info_block.strip(),
                "{cast}": actor_links or actor_names,
                "{cast_info}": cast_summary,
                "#DIRECTORS": director_links or director_names,
                "{director}": director_links or director_names,
                "#WRITERS": writer_links or writer_names,
                "{writer}": writer_links or writer_names,
                "#ACTORS": actor_links or actor_names,
                "{actor}": actor_links or actor_names,
                "#AWARDS": awards_text or "N/A",
                "{awards}": awards_text or "N/A",
                "#KEYWORD": keywords_plain_text or "N/A",
                "{keyword}": keywords_plain_text or "N/A",
                "{keywords}": keywords_block or "",
                "#OTT": ott or "N/A",
                "{ott}": ott or "N/A",
                "#OTT_UPDATES": ott,
                "#OTT_UPDATES_more": ott,
                "#HIGH_RES_MEDIA_VIEWER": poster or imdb_url,
                "#LETTERBOX_RATING": "",
                "#LETTERBOX_USERRATINGS": "",
                "{preview:disabled}": "",
                "{preview:large}": "",
                "{preview:small}": "",
                "{preview:top}": "",
            }
            caption_text = (
                _apply_template(template_text, template_data)
                if template_text
                else _build_default_caption("id", default_caption_data)
            )
            caption_mode = enums.ParseMode.HTML
            markup = (
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🎬 Open IMDB", url=imdb_url),
                            InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                        ]
                    ]
                )
                if trailer_url
                else InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)]]
                )
            )
            thumb = r_json.get("image")
            if thumb:
                try:
                    await query.message.edit_media(
                        InputMediaPhoto(
                            thumb,
                            caption=caption_text,
                            parse_mode=caption_mode,
                        ),
                        reply_markup=markup,
                    )
                except (PhotoInvalidDimensions, WebpageMediaEmpty, RPCError):
                    poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                    await query.message.edit_media(
                        InputMediaPhoto(
                            poster,
                            caption=caption_text,
                            parse_mode=caption_mode,
                        ),
                        reply_markup=markup,
                    )
                except (
                    MediaEmpty,
                    MediaCaptionTooLong,
                    WebpageCurlFailed,
                    MessageNotModified,
                    RPCError,
                ):
                    await query.message.reply(
                        caption_text, parse_mode=caption_mode, reply_markup=markup
                    )
                except Exception as err:
                    LOGGER.error(
                        f"Terjadi error saat menampilkan data IMDB. ERROR: {err}"
                    )
            else:
                await query.message.edit_caption(
                    caption_text, parse_mode=enums.ParseMode.HTML, reply_markup=markup
                )
        except httpx.HTTPError as exc:
            await query.message.edit_caption(
                f"HTTP Exception for IMDB Search - <code>{exc}</code>"
            )
        except AttributeError:
            await query.message.edit_caption(
                "Maaf, gagal mendapatkan info data dari IMDB."
            )
        except (MessageNotModified, MessageIdInvalid):
            pass


@app.on_cb("imdbres_en")
async def imdb_en_callback(self: Client, query: CallbackQuery):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    with contextlib.redirect_stdout(sys.stderr):
        try:
            await query.message.edit_caption("<i>⏳ Getting IMDb source..</i>")
            imdb_id = f"tt{movie}"
            imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
            resp = await fetch.get(imdb_url)
            resp.raise_for_status()
            sop = BeautifulSoup(resp, "lxml")
            r_json = json.loads(
                sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
            )
            title = r_json.get("name", "N/A")
            aka = r_json.get("alternateName", "") or "N/A"
            ott = await search_jw(
                r_json.get("alternateName") or r_json.get("name"), "US"
            )
            typee = r_json.get("@type", "")
            res_str = ""
            tahun = (
                r_json.get("datePublished", "").split("-")[0]
                if r_json.get("datePublished")
                else (
                    re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0]
                    if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)
                    else "N/A"
                )
            )
            rating_info = r_json.get("aggregateRating") or {}
            rating_value = str(rating_info.get("ratingValue", "N/A"))
            rating_count = rating_info.get("ratingCount")
            votes_text = _format_number(rating_count) if rating_count else "N/A"
            content_rating = r_json.get("contentRating", "N/A")
            duration_iso = r_json.get("duration")
            duration_text_raw = ""
            if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
                duration_text_raw = (
                    durasi[0]
                    .find(class_="ipc-metadata-list-item__content-container")
                    .text
                )
            duration_text, duration_seconds, duration_minutes, runtime_display = _parse_duration(
                duration_iso, duration_text_raw
            )
            rilis = ""
            rilis_url = ""
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
            genres_plain_list = r_json.get("genre") or []
            genres_plain = ", ".join(genres_plain_list) if genres_plain_list else "N/A"
            genres_hash = (
                "".join(
                    f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                    if i in GENRES_EMOJI
                    else f"#{i.replace('-', '_').replace(' ', '_')}, "
                    for i in genres_plain_list
                )[:-2]
                if genres_plain_list
                else ""
            )
            country_plain = "N/A"
            country_hash = ""
            if negara := sop.select('li[data-testid="title-details-origin"]'):
                countries_text = []
                countries_display = []
                for country in negara[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                ):
                    clean_country, display_country = _format_country_name(country.text)
                    if clean_country:
                        countries_text.append(clean_country)
                    if display_country:
                        countries_display.append(display_country)
                country_plain = ", ".join(countries_display) if countries_display else "N/A"
                country_hash = (
                    ", ".join(
                        f"#{country.replace(' ', '_').replace('-', '_')}" for country in countries_text
                    )
                    if countries_text
                    else ""
                )
            language_plain = "N/A"
            language_hash = ""
            if bahasa := sop.select('li[data-testid="title-details-languages"]'):
                languages = [
                    lang.text
                    for lang in bahasa[0].findAll(
                        class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                    )
                ]
                language_plain = ", ".join(languages)
                language_hash = ", ".join(
                    f"#{lang.replace(' ', '_').replace('-', '_')}" for lang in languages
                )
            director_links = ""
            director_names = ""
            if directors := r_json.get("director"):
                director_links = ", ".join(
                    f"<a href='{i['url']}'>{i['name']}</a>" for i in directors
                )
                director_names = ", ".join(i["name"] for i in directors)
            writer_links = ""
            writer_names = ""
            if creators := r_json.get("creator"):
                writer_links = ", ".join(
                    f"<a href='{i['url']}'>{i['name']}</a>"
                    for i in creators
                    if i["@type"] == "Person"
                )
                writer_names = ", ".join(
                    i["name"] for i in creators if i["@type"] == "Person"
                )
            actor_links = ""
            actor_names = ""
            if actors := r_json.get("actor"):
                actor_links = ", ".join(
                    f"<a href='{i['url']}'>{i['name']}</a>" for i in actors
                )
                actor_names = ", ".join(i["name"] for i in actors)
            summary = r_json.get("description", "") or ""
            short_desc = summary[:217] + "..." if len(summary) > 220 else summary
            awards_text = ""
            if award := sop.select('li[data-testid="award_information"]'):
                awards = (
                    award[0]
                    .find(class_="ipc-metadata-list-item__list-content-item")
                    .text
                )
                awards_text = awards
            keywords_block = ""
            keywords_plain_text = ""
            if r_json.get("keywords"):
                keywords_list = [i.strip() for i in r_json["keywords"].split(",") if i.strip()]
                keywords_block = (
                    "".join(
                        f"#{i.replace(' ', '_').replace('-', '_')}, "
                        for i in keywords_list
                    )[:-2]
                    if keywords_list
                    else ""
                )
                keywords_plain_text = ", ".join(keywords_list)
            trailer_url = r_json.get("trailer", {}).get("url", "")
            poster = r_json.get("image", "")
            cast_summary = _build_cast_summary(
                "en", html.escape(director_names or ""), html.escape(writer_names or ""), html.escape(actor_names or "")
            )
            default_caption_data = {
                "title": html.escape(title),
                "year": html.escape(tahun),
                "type": html.escape(typee),
                "runtime": html.escape(runtime_display),
                "content_rating": html.escape(content_rating or "N/A"),
                "rating": html.escape(rating_value),
                "votes": html.escape(votes_text),
                "release": html.escape(rilis or "N/A"),
                "genres": html.escape(genres_plain or "N/A"),
                "countries": html.escape(country_plain or "N/A"),
                "languages": html.escape(language_plain or "N/A"),
                "cast_info": cast_summary,
                "plot": html.escape(summary or "N/A"),
                "keywords": html.escape(keywords_plain_text or ""),
                "awards": html.escape(awards_text or ""),
                "ott": ott or "",
                "bot_username": html.escape(self.me.username),
            }
            cast_info_block = "\n<b>🙎 Cast Info:</b>\n"
            if director_links:
                cast_info_block += f"<b>Director:</b> {director_links}\n"
            if writer_links:
                cast_info_block += f"<b>Writer:</b> {writer_links}\n"
            if actor_links:
                cast_info_block += f"<b>Stars:</b> {actor_links}\n"
            if cast_info_block.strip() == "<b>🙎 Cast Info:</b>":
                cast_info_block += "N/A\n"
            plot_block = ""
            if summary:
                plot_block = f"<b>📜 Summary:</b>\n<blockquote><code>{summary}</code></blockquote>\n\n"
            res_str += f"<b>📹 Title:</b> <a href='{imdb_url}'>{title} [{tahun}]</a> (<code>{typee}</code>)\n"
            res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
            res_str += f"<b>Duration:</b> <code>{runtime_display}</code>\n"
            if content_rating:
                res_str += f"<b>Category:</b> <code>{content_rating}</code> \n"
            if rating_info:
                res_str += f"<b>Rating:</b> <code>{rating_value}⭐️ from {votes_text} users</code>\n"
            if rilis:
                res_str += f"<b>Release:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
            if genres_hash:
                res_str += f"<b>Genre:</b> {genres_hash}\n"
            if country_hash:
                res_str += f"<b>Country:</b> {country_hash}\n"
            if language_hash:
                res_str += f"<b>Language:</b> {language_hash}\n"
            res_str += cast_info_block
            if plot_block:
                res_str += plot_block
            if keywords_block:
                res_str += (
                    f"<b>🔥 Keywords:</b>\n<blockquote>{keywords_block}</blockquote>\n"
                )
            if awards_text:
                res_str += (
                    f"<b>🏆 Awards:</b>\n<blockquote><code>{awards_text}</code></blockquote>\n"
                )
            else:
                res_str += "\n"
            if ott != "":
                res_str += f"Available On:\n{ott}\n"
            res_str += f"<b>©️ IMDb by</b> @{self.me.username}"
            template_text = await get_imdb_template(query.from_user.id)
            template_data = {
                "#AKA": aka,
                "{aka}": aka,
                "#TITLE": title,
                "{title}": title,
                "#TYPE": typee,
                "{type}": typee,
                "#YEAR": tahun,
                "{year}": tahun,
                "#RATING": rating_value,
                "{rating}": rating_value,
                "#USER_RATING": votes_text,
                "{user_rating}": votes_text,
                "#EUSERRATINGS": f"{votes_text} IMDb users",
                "#NUMUSERRATINGS": votes_text,
                "#ONLYRATING": rating_value,
                "#VOTES": votes_text,
                "{votes}": votes_text,
                "#MARINTG": content_rating or "N/A",
                "#DURATION": runtime_display,
                "{duration}": runtime_display,
                "#DURATION_IN_SECONDS": duration_seconds,
                "#DURATION_IN_MINUTES": duration_minutes,
                "{runtime}": runtime_display,
                "#RELEASE_INFO": f"<a href='https://www.imdb.com{rilis_url}'>{rilis}</a>"
                if rilis
                else "N/A",
                "#RELEASE_DATE": rilis or "N/A",
                "{release_date}": rilis or "N/A",
                "#GENRE": genres_hash or genres_plain,
                "{genres}": genres_plain,
                "{genre}": genres_plain,
                "#IMDB_URL": imdb_url,
                "{url}": imdb_url,
                "#IMDB_ID": imdb_id,
                "{imdb_id}": imdb_id,
                "#IMDB_IV": f"<a href='{poster}'>&#8205;</a>" if poster else "",
                "#LANGUAGE": language_plain,
                "#COUNTRY_OF_ORIGIN": country_plain,
                "#LANG": language_plain,
                "#COUNTRY": country_plain,
                "{languages}": language_plain,
                "{language}": language_plain,
                "{countries}": country_plain,
                "{country}": country_plain,
                "#STORY_LINE": summary or "N/A",
                "{plot}": summary or "N/A",
                "{sinopsis}": summary or "N/A",
                "#IMDb_TITLE_TYPE": typee,
                "{kind}": typee,
                "#CATEGORY": content_rating or "N/A",
                "{category}": content_rating or "N/A",
                "#IMDb_SHORT_DESC": short_desc or summary or "N/A",
                "#READ_MORE": f"<a href='{imdb_url}'>Read more</a>",
                "#IMG_HIDDEN_IMG": f"<a href='{poster}'>&#8205;</a>" if poster else "",
                "#IMG_POSTER": poster or "",
                "{poster}": poster or "",
                "#TRAILER": trailer_url,
                "#CAST_INFO_": cast_info_block.strip(),
                "#DIRECTORS_": f"<b>Director:</b> {director_links}" if director_links else "",
                "#WRITERS_": f"<b>Writer:</b> {writer_links}" if writer_links else "",
                "#ACTORS_": f"<b>Stars:</b> {actor_links}" if actor_links else "",
                "#CAST_INFO": cast_info_block.strip(),
                "{cast}": actor_links or actor_names,
                "{cast_info}": cast_summary,
                "#DIRECTORS": director_links or director_names,
                "{director}": director_links or director_names,
                "#WRITERS": writer_links or writer_names,
                "{writer}": writer_links or writer_names,
                "#ACTORS": actor_links or actor_names,
                "{actor}": actor_links or actor_names,
                "#AWARDS": awards_text or "N/A",
                "{awards}": awards_text or "N/A",
                "#KEYWORD": keywords_plain_text or "N/A",
                "{keyword}": keywords_plain_text or "N/A",
                "{keywords}": keywords_block or "",
                "#OTT": ott or "N/A",
                "{ott}": ott or "N/A",
                "#OTT_UPDATES": ott,
                "#OTT_UPDATES_more": ott,
                "#HIGH_RES_MEDIA_VIEWER": poster or imdb_url,
                "#LETTERBOX_RATING": "",
                "#LETTERBOX_USERRATINGS": "",
                "{preview:disabled}": "",
                "{preview:large}": "",
                "{preview:small}": "",
                "{preview:top}": "",
            }
            caption_text = (
                _apply_template(template_text, template_data)
                if template_text
                else _build_default_caption("en", default_caption_data)
            )
            caption_mode = enums.ParseMode.HTML
            markup = (
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🎬 Open IMDB", url=imdb_url),
                            InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                        ]
                    ]
                )
                if trailer_url
                else InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)]]
                )
            )
            thumb = r_json.get("image")
            if thumb:
                try:
                    await query.message.edit_media(
                        InputMediaPhoto(
                            thumb,
                            caption=caption_text,
                            parse_mode=caption_mode,
                        ),
                        reply_markup=markup,
                    )
                except (PhotoInvalidDimensions, WebpageMediaEmpty, RPCError):
                    poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                    await query.message.edit_media(
                        InputMediaPhoto(
                            poster,
                            caption=caption_text,
                            parse_mode=caption_mode,
                        ),
                        reply_markup=markup,
                    )
                except (
                    MediaCaptionTooLong,
                    WebpageCurlFailed,
                    MediaEmpty,
                    MessageNotModified,
                    RPCError,
                ):
                    await query.message.reply(
                        caption_text, parse_mode=caption_mode, reply_markup=markup
                    )
                except Exception as err:
                    LOGGER.error(f"Error while displaying IMDB Data. ERROR: {err}")
            else:
                await query.message.edit_caption(
                    caption_text, parse_mode=enums.ParseMode.HTML, reply_markup=markup
                )
        except httpx.HTTPError as exc:
            await query.message.edit_caption(
                f"HTTP Exception for IMDB Search - <code>{exc}</code>"
            )
        except AttributeError:
            await query.message.edit_caption("Sorry, failed getting data from IMDB.")
        except (MessageNotModified, MessageIdInvalid):
            pass
