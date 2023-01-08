"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""

import os, re
import aiohttp
from bs4 import BeautifulSoup
import json
import traceback
from pyrogram import Client, filters
from deep_translator import GoogleTranslator
from gtts import gTTS
from pyrogram.errors import (
    MediaEmpty,
    MessageNotModified,
    PhotoInvalidDimensions,
    UserNotParticipant,
    WebpageMediaEmpty,
    MessageTooLong,
)
from utils import extract_user, get_file_id, demoji
import time
from datetime import datetime
from logging import getLogger
from pykeyboard import InlineKeyboard
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto,
)
from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.tools import rentry, GENRES_EMOJI
from misskaty.vars import COMMAND_HANDLER
from misskaty.helper.http import http
from misskaty import app, BOT_USERNAME

LOGGER = getLogger(__name__)

__MODULE__ = "Misc"
__HELP__ = """
/sof [query] - Search your problem in StackOverflow.
/google [query] - Search using Google Search.
(/tr, /trans, /translate) [lang code] - Translate text using Google Translate.
/tts - Convert Text to Voice.
/imdb [query] - Find Movie Details From IMDB.com in Indonesian Language.
/imdb_en [query] - Find Movie Details From IMDB.com in English Language.
"""


def remove_html_tags(text):
    """Remove html tags from a string"""
    import re

    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


@app.on_message(filters.command(["sof"], COMMAND_HANDLER))
@capture_err
async def stackoverflow(client, message):
    if len(message.command) == 1:
        return await message.reply("Give a query to search in StackOverflow!")
    r = (
        await http.get(
            f"https://api.stackexchange.com/2.3/search/excerpts?order=asc&sort=relevance&q={message.command[1]}&accepted=True&migrated=False¬ice=False&wiki=False&site=stackoverflow"
        )
    ).json()
    msg = await message.reply("Getting data..")
    hasil = ""
    for count, data in enumerate(r["items"], start=1):
        question = data["question_id"]
        title = data["title"]
        snippet = (
            remove_html_tags(data["excerpt"])[:80].replace("\n", "").replace("    ", "")
            if len(remove_html_tags(data["excerpt"])) > 80
            else remove_html_tags(data["excerpt"]).replace("\n", "").replace("    ", "")
        )
        hasil += f"{count}. <a href='https://stackoverflow.com/questions/{question}'>{title}</a>\n<code>{snippet}</code>\n"
    try:
        await msg.edit(hasil)
    except MessageTooLong:
        url = await rentry(hasil)
        await msg.edit(f"Your text pasted to rentry because has long text:\n{url}")
    except Exception as e:
        await msg.edit(e)


@app.on_message(filters.command(["google"], COMMAND_HANDLER))
@capture_err
async def gsearch(client, message):
    if len(message.command) == 1:
        return await message.reply("Give a query to search in Google!")
    query = message.text.split(" ", maxsplit=1)[1]
    msg = await message.reply_text(f"**Googling** for `{query}` ...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/61.0.3163.100 Safari/537.36"
        }
        html = await http.get(
            f"https://www.google.com/search?q={query}&gl=id&hl=id&num=17",
            headers=headers,
        )
        soup = BeautifulSoup(html.text, "lxml")

        # collect data
        data = []

        for result in soup.select(".tF2Cxc"):
            title = result.select_one(".DKV0Md").text
            link = result.select_one(".yuRUbf a")["href"]
            try:
                snippet = result.select_one("#rso .lyLwlc").text
            except:
                snippet = "-"

            # appending data to an array
            data.append(
                {
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                }
            )
        arr = json.dumps(data, indent=2, ensure_ascii=False)
        parse = json.loads(arr)
        total = len(parse)
        res = "".join(
            f"<a href='{i['link']}'>{i['title']}</a>\n{i['snippet']}\n\n" for i in parse
        )
    except Exception:
        exc = traceback.format_exc()
        return await msg.edit(exc)
    await msg.edit(
        text=f"<b>Ada {total} Hasil Pencarian dari {query}:</b>\n{res}<b>Scraped by @{BOT_USERNAME}</b>",
        disable_web_page_preview=True,
    )


@app.on_message(filters.command(["tr", "trans", "translate"], COMMAND_HANDLER))
@capture_err
async def translate(client, message):
    if message.reply_to_message and (
        message.reply_to_message.text or message.reply_to_message.caption
    ):
        target_lang = "id" if len(message.command) == 1 else message.text.split()[1]
        text = message.reply_to_message.text or message.reply_to_message.caption
    else:
        if len(message.command) < 3:
            return await message.reply_text(
                "Berikan Kode bahasa yang valid.\n[Available options](https://telegra.ph/Lang-Codes-11-08).\n<b>Usage:</b> <code>/tr en</code>",
            )
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    msg = await message.reply("Menerjemahkan...")
    my_translator = GoogleTranslator(source="auto", target=target_lang)
    try:
        result = my_translator.translate(text=text)
        await msg.edit(
            f"Translation using source = {my_translator.source} and target = {my_translator.target}\n\n-> {result}"
        )
    except MessageTooLong:
        url = await rentry(tekstr.text)
        await msg.edit(
            f"Your translated text pasted to rentry because has long text:\n{url}"
        )
    except Exception as err:
        await msg.edit(f"Error: <code>{str(err)}</code>")


@app.on_message(filters.command(["tts"], COMMAND_HANDLER))
@capture_err
async def tts(_, message):
    if message.reply_to_message and (
        message.reply_to_message.text or message.reply_to_message.caption
    ):
        if len(message.text.split()) == 1:
            target_lang = "id"
        else:
            target_lang = message.text.split()[1]
        text = message.reply_to_message.text or message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            await message.reply_text(
                "Berikan Kode bahasa yang valid.\n[Available options](https://telegra.ph/Lang-Codes-11-08).\n*Usage:* /tts en [text]",
            )
            return
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    msg = await message.reply("Converting to voice...")
    try:
        tts = gTTS(text, lang=target_lang)
        tts.save(f"tts_{message.from_user.id}.mp3")
    except ValueError as err:
        await msg.edit(f"Error: <code>{str(err)}</code>")
        return
    await msg.delete()
    await msg.reply_audio(f"tts_{message.from_user.id}.mp3")
    try:
        os.remove(f"tts_{message.from_user.id}.mp3")
    except:
        pass


@app.on_message(filters.command(["tosticker"], COMMAND_HANDLER))
@capture_err
async def tostick(client, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply_text("Reply ke foto untuk mengubah ke sticker")
        sticker = await client.download_media(
            message.reply_to_message.photo.file_id,
            f"tostick_{message.from_user.id}.webp",
        )
        await message.reply_sticker(sticker)
        os.remove(sticker)
    except Exception as e:
        await message.reply_text(str(e))


@app.on_message(filters.command(["toimage"], COMMAND_HANDLER))
@capture_err
async def topho(client, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.sticker:
            return await message.reply_text("Reply ke sticker untuk mengubah ke foto")
        if message.reply_to_message.sticker.is_animated:
            return await message.reply_text(
                "Ini sticker animasi, command ini hanya untuk sticker biasa."
            )
        photo = await client.download_media(
            message.reply_to_message.sticker.file_id,
            f"tostick_{message.from_user.id}.jpg",
        )
        await message.reply_photo(
            photo=photo, caption="Sticker -> Image\n@{BOT_USERNAME}"
        )

        os.remove(photo)
    except Exception as e:
        await message.reply_text(str(e))


@app.on_message(filters.command(["id"], COMMAND_HANDLER))
async def showid(client, message):
    chat_type = message.chat.type
    if chat_type == "private":
        user_id = message.chat.id
        first = message.from_user.first_name
        last = message.from_user.last_name or ""
        username = message.from_user.username
        dc_id = message.from_user.dc_id or ""
        await message.reply_text(
            f"<b>➲ First Name:</b> {first}\n<b>➲ Last Name:</b> {last}\n<b>➲ Username:</b> {username}\n<b>➲ Telegram ID:</b> <code>{user_id}</code>\n<b>➲ Data Centre:</b> <code>{dc_id}</code>",
            quote=True,
        )

    elif chat_type in ["group", "supergroup"]:
        _id = ""
        _id += "<b>➲ Chat ID</b>: " f"<code>{message.chat.id}</code>\n"
        if message.reply_to_message:
            _id += (
                "<b>➲ User ID</b>: "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
                "<b>➲ Replied User ID</b>: "
                f"<code>{message.reply_to_message.from_user.id if message.reply_to_message.from_user else 'Anonymous'}</code>\n"
            )
            file_info = get_file_id(message.reply_to_message)
        else:
            _id += (
                "<b>➲ User ID</b>: "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
            )
            file_info = get_file_id(message)
        if file_info:
            _id += (
                f"<b>{file_info.message_type}</b>: "
                f"<code>{file_info.file_id}</code>\n"
            )
        await message.reply_text(_id, quote=True)


@app.on_message(filters.command(["info"], COMMAND_HANDLER))
async def who_is(client, message):
    # https://github.com/SpEcHiDe/PyroGramBot/blob/master/pyrobot/plugins/admemes/whois.py#L19
    status_message = await message.reply_text("`Fetching user info...`")
    await status_message.edit("`Processing user info...`")
    from_user = None
    from_user_id, _ = extract_user(message)
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(str(error))
        return
    if from_user is None:
        return await status_message.edit("no valid user_id / message specified")
    message_out_str = ""
    message_out_str += f"<b>➲First Name:</b> {from_user.first_name}\n"
    last_name = from_user.last_name or "<b>None</b>"
    message_out_str += f"<b>➲Last Name:</b> {last_name}\n"
    message_out_str += f"<b>➲Telegram ID:</b> <code>{from_user.id}</code>\n"
    username = from_user.username or "<b>None</b>"
    dc_id = from_user.dc_id or "[User Doesnt Have A Valid DP]"
    message_out_str += f"<b>➲Data Centre:</b> <code>{dc_id}</code>\n"
    message_out_str += f"<b>➲User Name:</b> @{username}\n"
    message_out_str += f"<b>➲User 𝖫𝗂𝗇𝗄:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"
    if message.chat.type in (("supergroup", "channel")):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = datetime.fromtimestamp(
                chat_member_p.joined_date or time.time()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += (
                "<b>➲Joined this Chat on:</b> <code>" f"{joined_date}" "</code>\n"
            )
        except UserNotParticipant:
            pass
    if chat_photo := from_user.photo:
        local_user_photo = await client.download_media(message=chat_photo.big_file_id)
        buttons = [
            [
                InlineKeyboardButton(
                    "🔐 Close", callback_data=f"close#{message.from_user.id}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=reply_markup,
            caption=message_out_str,
            disable_notification=True,
        )
        os.remove(local_user_photo)
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    "🔐 Close", callback_data=f"close#{message.from_user.id}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            quote=True,
            disable_notification=True,
        )
    await status_message.delete()


@app.on_callback_query(filters.regex("^close"))
async def close_callback(bot: Client, query: CallbackQuery):
    i, userid = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    await query.message.delete()


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"
}


async def get_content(url):
    async with aiohttp.ClientSession() as session:
        r = await session.get(url, headers=headers)
        return await r.read()


async def mdlapi(title):
    link = f"https://kuryana.vercel.app/search/q/{title}"
    async with aiohttp.ClientSession() as ses:
        async with ses.get(link) as result:
            return await result.json()


@app.on_message(filters.command(["mdl"], COMMAND_HANDLER))
@capture_err
async def mdlsearch(client, message):
    if " " in message.text:
        r, title = message.text.split(None, 1)
        k = await message.reply("Sedang mencari di Database MyDramaList.. 😴")
        movies = await mdlapi(title)
        res = movies["results"]["dramas"]
        if not movies:
            return await k.edit("Tidak ada hasil ditemukan.. 😕")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} ({movie.get('year')})",
                    callback_data=f"mdls#{message.from_user.id}#{message.id}#{movie['slug']}",
                )
            ]
            for movie in res
        ]
        await k.edit(
            f"Ditemukan {len(movies)} query dari <code>{title}</code>",
            reply_markup=InlineKeyboardMarkup(btn),
        )
    else:
        await message.reply("Berikan aku nama drama yang ingin dicari. 🤷🏻‍♂️")


@app.on_callback_query(filters.regex("^mdls"))
@capture_err
async def mdl_callback(bot: Client, query: CallbackQuery):
    i, user, msg_id, slug = query.data.split("#")
    if user == f"{query.from_user.id}":
        await query.message.edit_text("Permintaan kamu sedang diproses.. ")
        result = ""
        try:
            res = (await http.get(f"https://kuryana.vercel.app/id/{slug}")).json()
            result += f"<b>Title:</b> <a href='{res['data']['link']}'>{res['data']['title']}</a>\n"
            result += (
                f"<b>AKA:</b> <code>{res['data']['others']['also_known_as']}</code>\n\n"
            )
            result += f"<b>Rating:</b> <code>{res['data']['details']['score']}</code>\n"
            result += f"<b>Content Rating:</b> <code>{res['data']['details']['content_rating']}</code>\n"
            result += f"<b>Type:</b> <code>{res['data']['details']['type']}</code>\n"
            result += (
                f"<b>Country:</b> <code>{res['data']['details']['country']}</code>\n"
            )
            if res["data"]["details"]["type"] == "Movie":
                result += f"<b>Release Date:</b> <code>{res['data']['details']['release_date']}</code>\n"
            elif res["data"]["details"]["type"] == "Drama":
                result += f"<b>Episode:</b> {res['data']['details']['episodes']}\n"
                result += (
                    f"<b>Aired:</b> <code>{res['data']['details']['aired']}</code>\n"
                )
                try:
                    result += f"<b>Aired on:</b> <code>{res['data']['details']['aired_on']}</code>\n"
                except:
                    pass
                try:
                    result += f"<b>Original Network:</b> <code>{res['data']['details']['original_network']}</code>\n"
                except:
                    pass
            result += (
                f"<b>Duration:</b> <code>{res['data']['details']['duration']}</code>\n"
            )
            result += (
                f"<b>Genre:</b> <code>{res['data']['others']['genres']}</code>\n\n"
            )
            result += f"<b>Synopsis:</b> <code>{res['data']['synopsis']}</code>\n"
            result += f"<b>Tags:</b> <code>{res['data']['others']['tags']}</code>\n"
            btn = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎬 Open MyDramaList", url=res["data"]["link"])]]
            )
            await query.message.edit_text(result, reply_markup=btn)
        except Exception as e:
            await query.message.edit_text(f"<b>ERROR:</b>\n<code>{e}</code>")
    else:
        await query.answer("Tombol ini bukan untukmu", show_alert=True)


# IMDB Versi Indonesia v1
@app.on_message(filters.command(["imdb"], COMMAND_HANDLER))
@capture_err
async def imdb1_search(client, message):
    BTN = []
    if message.sender_chat:
        return await message.reply(
            "Mohon maaf fitur tidak tersedia untuk akun channel, harap ganti ke akun biasa.."
        )
    if len(message.command) == 1:
        return await message.reply(
            "Berikan aku nama series atau movie yang ingin dicari. 🤷🏻‍♂️", quote=True
        )
    r, judul = message.text.split(None, 1)
    k = await message.reply_photo(
        "https://telegra.ph/file/270955ef0d1a8a16831a9.jpg",
        caption="🔎 Sedang mencari di Database IMDB..",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await get_content(f"https://yasirapi.eu.org/imdb-search?q={judul}")
        res = json.loads(r).get("result")
        if not res:
            return await k.edit_caption("Tidak ada hasil ditemukan.. 😕")
        msg += f"Ditemukan {len(res)} query dari <code>{judul}</code> ~ {message.from_user.mention}\n\n"
        for count, movie in enumerate(res, start=1):
            title = movie.get("l")
            year = f"({movie.get('y')})" if movie.get("y") else ""
            type = movie.get("q").replace("feature", "movie").capitalize()
            movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
            msg += f"{count}. {title} {year} ~ {type}\n"
            BTN.append(
                InlineKeyboardButton(
                    text=count, callback_data=f"imdbid#{message.from_user.id}#{movieID}"
                )
            )
        BTN.append(
            InlineKeyboardButton(
                text="❌ Close", callback_data=f"close#{message.from_user.id}"
            )
        )
        buttons.add(*BTN)
        await k.edit_caption(msg, reply_markup=buttons)
    except Exception as err:
        await k.edit_caption(
            f"Ooppss, gagal mendapatkan daftar judul di IMDb.\n\nERROR: {err}"
        )


@app.on_callback_query(filters.regex("^imdbid"))
async def imdbcb_backup(bot: Client, query: CallbackQuery):
    # ValueError: not enough values to unpack (expected 3, got 2)
    # Idk how to reproduce it, so wait people report to me
    try:
        i, userid, movie = query.data.split("#")
    except:
        LOGGER.error(
            f"ERROR IMDB Callback: {query.data} - {query.from_user.first_name} [{query.from_user.id}]"
        )
        return await query.answer(
            "⚠️ Invalid callback query, silahkan laporkan ke pemilik bot atau buka issue baru di repository MissKaty dengan alasan yang jelas.",
            True,
        )
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    try:
        await query.message.edit_caption("⏳ Permintaan kamu sedang diproses.. ")
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await get_content(url)
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(
            sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
        )
        res_str = ""
        type = f"<code>{r_json['@type']}</code>" if r_json.get("@type") else ""
        if r_json.get("name"):
            try:
                tahun = (
                    sop.select('ul[data-testid="hero-title-block__metadata"]')[0]
                    .find(class_="sc-8c396aa2-2 itZqyK")
                    .text
                )
            except:
                tahun = "-"
            res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json['name']} [{tahun}]</a> (<code>{type}</code>)\n"
        if r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
        else:
            res_str += "\n"
        if sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = (
                sop.select('li[data-testid="title-techspec_runtime"]')[0]
                .find(class_="ipc-metadata-list-item__content-container")
                .text
            )
            res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>Kategori:</b> <code>{r_json['contentRating']}</code> \n"
        if r_json.get("aggregateRating"):
            res_str += f"<b>Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
        if sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = (
                sop.select('li[data-testid="title-details-releasedate"]')[0]
                .find(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
                .text
            )
            rilis_url = sop.select('li[data-testid="title-details-releasedate"]')[
                0
            ].find(
                class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
            )[
                "href"
            ]
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
                for country in sop.select('li[data-testid="title-details-origin"]')[
                    0
                ].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
            country = country[:-2]
            res_str += f"<b>Negara:</b> {country}\n"
        if sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(
                f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                for lang in sop.select('li[data-testid="title-details-languages"]')[
                    0
                ].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
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
                r_json.get("description")
            )
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
                sop.select('li[data-testid="award_information"]')[0]
                .find(class_="ipc-metadata-list-item__list-content-item")
                .text
            )
            res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(awards)}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if r_json.get("trailer"):
            trailer_url = r_json["trailer"]["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"
                        ),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"
                        )
                    ]
                ]
            )
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(
                    InputMediaPhoto(thumb, caption=res_str), reply_markup=markup
                )
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(
                    InputMediaPhoto(poster, caption=res_str), reply_markup=markup
                )
            except Exception:
                await query.message.edit_caption(res_str, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, reply_markup=markup)
    except MessageNotModified:
        pass
    except Exception:
        exc = traceback.format_exc()
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")


# IMDB Versi English
@app.on_message(filters.command(["imdb_en"], COMMAND_HANDLER))
@capture_err
async def imdb_en_search(client, message):
    BTN = []
    if message.sender_chat:
        return await message.reply("This feature not available for channel.")
    if len(message.command) == 1:
        return await message.reply(
            "Give movie name or series. Ex: <code>/imdb_en soul</code>. 🤷🏻‍♂️",
            quote=True,
        )
    r, title = message.text.split(None, 1)
    k = await message.reply_photo(
        "https://telegra.ph/file/270955ef0d1a8a16831a9.jpg",
        caption="Searching Movie/Series in IMDB Database.. 😴",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    try:
        r = await get_content(f"https://yasirapi.eu.org/imdb-search?q={title}")
        res = json.loads(r).get("result")
        if not res:
            return await k.edit_caption("Sad, No Result.. 😕")
        msg = f"Found {len(res)} result from <code>{title}</code> ~ {message.from_user.mention}\n\n"
        for count, movie in enumerate(res, start=1):
            titles = movie.get("l")
            year = f"({movie.get('y')})" if movie.get("y") else ""
            type = movie.get("qid").replace("feature", "movie").capitalize()
            movieID = re.findall(r"tt(\d+)", movie.get("id"))[0]
            msg += f"{count}. {titles} {year} ~ {type}\n"
            BTN.append(
                InlineKeyboardButton(
                    text=count, callback_data=f"imdben#{message.from_user.id}#{movieID}"
                )
            )
        BTN.append(
            InlineKeyboardButton(
                text="❌ Close", callback_data=f"close#{message.from_user.id}"
            )
        )
        buttons.add(*BTN)
        await k.edit_caption(msg, reply_markup=buttons)
    except Exception as err:
        await k.edit_caption(
            f"Ooppss, failed get movie list from IMDb.\n\nERROR: {err}"
        )


@app.on_callback_query(filters.regex("^imdben"))
@capture_err
async def imdb_en_callback(bot: Client, query: CallbackQuery):
    try:
        i, userid, movie = query.data.split("#")
    except:
        LOGGER.error(
            f"ERROR IMDB Callback: {query.data} - {query.from_user.first_name} [{query.from_user.id}]"
        )
        return await query.answer(
            "⚠️ Invalid callback query, please report to bot owner or open issue in MissKaty repository with relevant details.",
            True,
        )
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    await query.message.edit_caption("<i>⏳ Processing your request..</i>")
    try:
        url = f"https://www.imdb.com/title/tt{movie}/"
        resp = await get_content(url)
        sop = BeautifulSoup(resp, "lxml")
        r_json = json.loads(
            sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
        )
        res_str = ""
        type = f"<code>{r_json['@type']}</code>" if r_json.get("@type") else ""
        if r_json.get("name"):
            try:
                tahun = (
                    sop.select('ul[data-testid="hero-title-block__metadata"]')[0]
                    .find(class_="sc-8c396aa2-2 itZqyK")
                    .text
                )
            except:
                tahun = "-"
            res_str += f"<b>📹 Title:</b> <a href='{url}'>{r_json['name']} [{tahun}]</a> (<code>{type}</code>)\n"
        if r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
        else:
            res_str += "\n"
        if sop.select('li[data-testid="title-techspec_runtime"]'):
            durasi = (
                sop.select('li[data-testid="title-techspec_runtime"]')[0]
                .find(class_="ipc-metadata-list-item__content-container")
                .text
            )
            res_str += f"<b>Duration:</b> <code>{durasi}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>Category:</b> <code>{r_json['contentRating']}</code> \n"
        if r_json.get("aggregateRating"):
            res_str += f"<b>Rating:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ from {r_json['aggregateRating']['ratingCount']} user</code> \n"
        if sop.select('li[data-testid="title-details-releasedate"]'):
            rilis = (
                sop.select('li[data-testid="title-details-releasedate"]')[0]
                .find(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
                .text
            )
            rilis_url = sop.select('li[data-testid="title-details-releasedate"]')[
                0
            ].find(
                class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
            )[
                "href"
            ]
            res_str += f"<b>Release Data:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
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
                for country in sop.select('li[data-testid="title-details-origin"]')[
                    0
                ].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
            )
            country = country[:-2]
            res_str += f"<b>Country:</b> {country}\n"
        if sop.select('li[data-testid="title-details-languages"]'):
            language = "".join(
                f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                for lang in sop.select('li[data-testid="title-details-languages"]')[
                    0
                ].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
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
            awards = (
                sop.select('li[data-testid="award_information"]')[0]
                .find(class_="ipc-metadata-list-item__list-content-item")
                .text
            )
            res_str += f"<b>🏆 Awards:</b> <code>{awards}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"<b>©️ IMDb by</b> @{BOT_USERNAME}"
        if r_json.get("trailer"):
            trailer_url = r_json["trailer"]["url"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"
                        ),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎬 Open IMDB", url=f"https://www.imdb.com{r_json['url']}"
                        )
                    ]
                ]
            )
        if thumb := r_json.get("image"):
            try:
                await query.message.edit_media(
                    InputMediaPhoto(thumb, caption=res_str), reply_markup=markup
                )
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                await query.message.edit_media(
                    InputMediaPhoto(poster, caption=res_str), reply_markup=markup
                )
            except Exception:
                await query.message.edit_caption(res_str, reply_markup=markup)
        else:
            await query.message.edit_caption(res_str, reply_markup=markup)
    except Exception:
        exc = traceback.format_exc()
        await query.message.edit_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")
