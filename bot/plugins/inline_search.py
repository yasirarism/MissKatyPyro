import requests
import json
from bot import app
from bot.plugins.misc import get_content
from utils import get_poster
from pyrogram import filters, enums
from bs4 import BeautifulSoup
from gpytranslate import Translator
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, InputTextMessageContent


@app.on_inline_query(
    filters.create(
        lambda _, __, inline_query:
        (inline_query.query and inline_query.query.startswith("imdb ") and
         inline_query.from_user),
        # https://t.me/UserGeSpam/359404
        name="ImdbInlineFilter"),
    group=-1)
async def inline_fn(_, inline_query: InlineQuery):
    movie_name = inline_query.query.split("imdb ")[1].strip()
    search_results = requests.get(
        f"https://betterimdbot.herokuapp.com/search.php?_={movie_name}")
    srch_results = json.loads(search_results.text)
    asroe = srch_results.get("d")
    oorse = []
    for sraeo in asroe:
        title = sraeo.get("l", "")
        description = sraeo.get("q", "")
        stars = sraeo.get("s", "")
        imdb_url = f"https://imdb.com/title/{sraeo.get('id')}"
        year = sraeo.get("yr", "").rstrip('-')
        try:
            image_url = sraeo.get("i").get("imageUrl")
        except:
            image_url = "https://te.legra.ph/file/e263d10ff4f4426a7c664.jpg"
        message_text = f"<a href='{image_url}'>🎬</a>"
        message_text += f"<a href='{imdb_url}'>{title} {year}</a>"
        oorse.append(
            InlineQueryResultArticle(
                title=f" {title} {year}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False),
                url=imdb_url,
                description=f" {description} | {stars}",
                thumb_url=image_url,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Get IMDB details",
                        callback_data=
                        f"imdbinl_{inline_query.from_user.id}_{sraeo.get('id')}"
                    )
                ]])))
    resfo = srch_results.get("q")
    await inline_query.answer(
        results=oorse,
        cache_time=300,
        is_gallery=False,
        is_personal=False,
        next_offset="",
        switch_pm_text=f"Found {len(oorse)} results for {resfo}",
        switch_pm_parameter="imdb")
    inline_query.stop_propagation()


@app.on_inline_query(filters.create(
    lambda _, __, inline_query: (inline_query.query and inline_query.query.
                                 startswith("yt ") and inline_query.from_user),
    name="YtInlineFilter"),
                     group=-1)
async def inline_fn(_, inline_query: InlineQuery):
    judul = inline_query.query.split("yt ")[1].strip()
    search_results = requests.get(
        f"https://api.abir-hasan.tk/youtube?query={judul}")
    srch_results = json.loads(search_results.text)
    asroe = srch_results.get("results")
    oorse = []
    for sraeo in asroe:
        title = sraeo.get("title")
        link = sraeo.get("link")
        view = sraeo["viewCount"]['text']
        deskripsi = "".join(f"{i['text']} "
                            for i in sraeo['results'][0]['descriptionSnippet'])
        message_text = f"<a href='{link}'>{title}</a>\n"
        message_text += f"Deskripsi: {deskripsi}\n"
        message_text += f"Jumlah View: {view}"
        oorse.append(
            InlineQueryResultArticle(
                title=f"{title}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False),
                url=link,
                description=deskripsi,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Open YT Link", url=link)]])))
    await inline_query.answer(results=oorse,
                              cache_time=300,
                              is_gallery=False,
                              is_personal=False,
                              next_offset="",
                              switch_pm_text=f"Found {len(asroe)} results",
                              switch_pm_parameter="yt")
    inline_query.stop_propagation()


@app.on_callback_query(filters.regex('^imdbinl_'))
async def imdb_inl(_, query):
    i, user, movie = query.data.split('_')
    if user == f"{query.from_user.id}":
        trl = Translator()
        url = f"https://www.imdb.com/title/{movie}/"
        imdb = await get_poster(query=movie.split("tt")[1], id=True)
        resp = await get_content(url)
        b = BeautifulSoup(resp, "lxml")
        r_json = json.loads(
            b.find("script", attrs={
                "type": "application/ld+json"
            }).contents[0])
        res_str = ""
        type = f"<code>{r_json['@type']}</code>" if r_json.get("@type") else ""
        if r_json.get("name"):
            res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json['name']}</a> (<code>{type}</code>)\n"
        if r_json.get("alternateName"):
            res_str += f"<b>📢 AKA:</b> <code>{r_json['alternateName']}</code>\n\n"
        else:
            res_str += "\n"
        if imdb.get("kind") == "tv series":
            res_str += f"<b>🍂 Total Season:</b> <code>{imdb['seasons']} season</code>\n"
        if r_json.get("duration"):
            durasi = r_json['duration'].replace("PT", "").replace(
                "H", " Jam ").replace("M", " Menit")
            res_str += f"<b>🕓 Durasi:</b> <code>{durasi}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>🔞 Content Rating:</b> <code>{r_json['contentRating']}</code> \n"
        if r_json.get("aggregateRating"):
            res_str += f"<b>🏆 Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']} dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
        if imdb.get("release_date"):
            res_str += f"<b>📆 Rilis:</b> <code>{imdb['release_date']}</code>\n"
        if r_json.get("genre"):
            all_genre = r_json['genre']
            genre = "".join(f"#{i}, " for i in all_genre)
            genre = genre[:-2].replace("-", "_")
            res_str += f"<b>🎭 Genre:</b> {genre}\n"
        if imdb.get("countries"):
            country = imdb['countries'].replace("  ", " ")
            if country.endswith(", "): country = country[:-2]
            res_str += f"<b>🆔 Negara:</b> <code>{country}</code>\n"
        if imdb.get("languages"):
            language = imdb['languages'].replace("  ", " ")
            if language.endswith(", "): language = language[:-2]
            res_str += f"<b>🔊 Bahasa:</b> <code>{language}</code>\n"
        if r_json.get("director"):
            all_director = r_json['director']
            director = "".join(f"{i['name']}, " for i in all_director)
            director = director[:-2]
            res_str += f"<b>Sutradara:</b> <code>{director}</code>\n"
        if r_json.get("actor"):
            all_actors = r_json['actor']
            actors = "".join(f"{i['name']}, " for i in all_actors)
            actors = actors[:-2]
            res_str += f"<b>Pemeran:</b> <code>{actors}</code>\n\n"
        if r_json.get("description"):
            summary = await trl(r_json['description'].replace("  ", " "),
                                targetlang='id')
            res_str += f"<b>📜 Plot: </b> <code>{summary.text}</code>\n\n"
        if r_json.get("keywords"):
            keywords = r_json['keywords'].split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Keyword/Tags:</b> {key_} \n\n"
        res_str += "<b>IMDb Feature by</b> @MissKatyRoBot"
        if r_json.get("trailer"):
            trailer_url = "https://imdb.com" + r_json['trailer']['embedUrl']
            markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🎬 Open IMDB", url=f"https://www.imdb.com/title/{movie}/"),
                InlineKeyboardButton("▶️ Trailer", url=trailer_url)
            ]])
        else:
            markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🎬 Open IMDB",
                    url=f"https://www.imdb.com/title/tt{movie}/")
            ]])
        await query.edit_message_text(res_str,
                                      reply_markup=markup,
                                      disable_web_page_preview=False)
    else:
        await query.answer("Tombol ini bukan untukmu", show_alert=True)
