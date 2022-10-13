import json, traceback
from bot import app
from bot.plugins.other_tools import get_content
from bot.helper.http import http
from pyrogram import filters, enums
from bs4 import BeautifulSoup
from utils import demoji
from deep_translator import GoogleTranslator
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto

__MODULE__ = "InlineFeature"
__HELP__ = """
To use this feature, just type bot username with following args below.
~ imdb [query] - Search movie details in IMDb.com.
~ pypi [query] - Search package from Pypi.
~ git [query] - Search in Git.
~ google [query] - Search in Google.
"""

keywords_list = [
    "imdb",
    "pypi",
    "git",
    "google",
]

@app.on_inline_query(
    filters.create(
        lambda _, __, inline_query:
        (inline_query.query and inline_query.query.startswith("imdb ") and
         inline_query.from_user),
        # https://t.me/UserGeSpam/359404
        name="ImdbInlineFilter",
    ),
    group=-1,
)
async def inline_fn(_, inline_query: InlineQuery):
    movie_name = inline_query.query.split("imdb ")[1].strip()
    search_results = await http.get(
        f"https://yasirapi.eu.org/imdb-search?q={movie_name}")
    res = json.loads(search_results.text).get('result')
    oorse = []
    for midb in res:
        title = midb.get("l", "")
        description = midb.get("q", "")
        stars = midb.get("s", "")
        imdb_url = f"https://imdb.com/title/{midb.get('id')}"
        year = f"({midb.get('y')})" if midb.get("y") else ""
        try:
            image_url = midb.get("i").get("imageUrl")
        except:
            image_url = "https://te.legra.ph/file/e263d10ff4f4426a7c664.jpg"
        caption = f"<a href='{image_url}'>🎬</a>"
        caption += f"<a href='{imdb_url}'>{title} {year}</a>"
        oorse.append(
            InlineQueryResultPhoto(
                title=f"{title} {year}",
                caption=caption,
                description=f" {description} | {stars}",
                photo_url=image_url,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Get IMDB details",
                        callback_data=
                        f"imdbin_{inline_query.from_user.id}_{midb.get('id')}"
                    )
                ]]),
            ))
    resfo = json.loads(search_results.text).get('q')
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
    search_results = await http.get(
        f"https://api.abir-hasan.tk/youtube?query={judul}")
    srch_results = json.loads(search_results.text)
    asroe = srch_results.get("results")
    oorse = []
    for sraeo in asroe:
        title = sraeo.get("title")
        link = sraeo.get("link")
        view = sraeo.get("viewCount").get("text")
        thumb = sraeo.get("thumbnails")[0].get("url")
        durasi = sraeo.get("accessibility").get("duration")
        publishTime = sraeo.get("publishedTime")
        try:
            deskripsi = "".join(f"{i['text']} "
                                for i in sraeo.get("descriptionSnippet"))
        except:
            deskripsi = "-"
        message_text = f"<a href='{link}'>{title}</a>\n"
        message_text += f"Description: {deskripsi}\n"
        message_text += f"Total View: {view}\n"
        message_text += f"Duration: {durasi}\n"
        message_text += f"Published Time: {publishTime}"
        oorse.append(
            InlineQueryResultArticle(
                title=f"{title}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False),
                url=link,
                description=deskripsi,
                thumb_url=thumb,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Watch Video 📹", url=link)]]),
            ))
    await inline_query.answer(results=oorse,
                              cache_time=300,
                              is_gallery=False,
                              is_personal=False,
                              next_offset="",
                              switch_pm_text=f"Found {len(asroe)} results",
                              switch_pm_parameter="yt")
    inline_query.stop_propagation()


@app.on_inline_query(
    filters.create(lambda _, __, inline_query:
                   (inline_query.query and inline_query.query.startswith(
                       "google ") and inline_query.from_user),
                   name="GoogleInlineFilter"),
    group=-1)
async def inline_fn(_, inline_query: InlineQuery):
    judul = inline_query.query.split("google ")[1].strip()
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/61.0.3163.100 Safari/537.36"
    }
    search_results = await http.get(f"https://www.google.com/search?q={judul}",
                                    headers=headers)
    soup = BeautifulSoup(search_results.text, "lxml")
    data = []
    for result in soup.select(".tF2Cxc"):
        title = result.select_one(".DKV0Md").text
        link = result.select_one(".yuRUbf a")["href"]
        try:
            snippet = result.select_one("#rso .lyLwlc").text
        except:
            snippet = "-"
        message_text = f"<a href='{link}'>{title}</a>\n"
        message_text += f"Deskription: {snippet}"
        data.append(
            InlineQueryResultArticle(
                title=f"{title}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False),
                url=link,
                description=snippet,
                thumb_url="https://te.legra.ph/file/ed8ea62ae636793000bb4.jpg",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Open Website", url=link)]]),
            ))
    await inline_query.answer(results=data,
                              cache_time=300,
                              is_gallery=False,
                              is_personal=False,
                              next_offset="",
                              switch_pm_text=f"Found {len(data)} results",
                              switch_pm_parameter="google")
    inline_query.stop_propagation()


@app.on_inline_query(
    filters.create(lambda _, __, inline_query:
                   (inline_query.query and inline_query.query.startswith(
                       "pypi ") and inline_query.from_user),
                   name="YtInlineFilter"),
    group=-1)
async def inline_fn(_, inline_query: InlineQuery):
    query = inline_query.query.split("pypi ")[1].strip()
    search_results = await http.get(
        f"https://api.hayo.my.id/api/pypi?package={query}")
    srch_results = json.loads(search_results.text)
    data = []
    for sraeo in srch_results:
        title = sraeo.get("title")
        link = sraeo.get("link")
        deskripsi = sraeo.get("desc")
        version = sraeo.get("version")
        message_text = f"<a href='{link}'>{title} {version}</a>\n"
        message_text += f"Description: {deskripsi}\n"
        data.append(
            InlineQueryResultArticle(
                title=f"{title}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False),
                url=link,
                description=deskripsi,
                thumb_url=
                "https://raw.githubusercontent.com/github/explore/666de02829613e0244e9441b114edb85781e972c/topics/pip/pip.png",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Open Link", url=link)]]),
            ))
    await inline_query.answer(results=data,
                              cache_time=300,
                              is_gallery=False,
                              is_personal=False,
                              next_offset="",
                              switch_pm_text=f"Found {len(data)} results",
                              switch_pm_parameter="pypi")
    inline_query.stop_propagation()


@app.on_inline_query(
    filters.create(lambda _, __, inline_query:
                   (inline_query.query and inline_query.query.startswith(
                       "git ") and inline_query.from_user),
                   name="GitInlineFilter"),
    group=-1)
async def inline_fn(_, inline_query: InlineQuery):
    query = inline_query.query.split("git ")[1].strip()
    search_results = await http.get(
        f"https://api.github.com/search/repositories?q={query}")
    srch_results = json.loads(search_results.text)
    item = srch_results.get("items")
    data = []
    for sraeo in item:
        title = sraeo.get("full_name")
        link = sraeo.get("html_url")
        deskripsi = sraeo.get("description")
        lang = sraeo.get("language")
        message_text = f"🔗: {sraeo.get('html_url')}\n│\n└─🍴Forks: {sraeo.get('forks')}    ┃┃    🌟Stars: {sraeo.get('stargazers_count')}\n\n"
        message_text += f"<b>Description:</b> {deskripsi}\n"
        message_text += f"<b>Language:</b> {lang}"
        data.append(
            InlineQueryResultArticle(
                title=f"{title}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=False),
                url=link,
                description=deskripsi,
                thumb_url=
                "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Open Github Link",
                                           url=link)]]),
            ))
    await inline_query.answer(results=data,
                              cache_time=300,
                              is_gallery=False,
                              is_personal=False,
                              next_offset="",
                              switch_pm_text=f"Found {len(data)} results",
                              switch_pm_parameter="github")
    inline_query.stop_propagation()


@app.on_callback_query(filters.regex("^imdbinl_"))
async def imdb_inl(_, query):
        i, user, movie = query.data.split("_")
        if user == f"{query.from_user.id}":
            await query.edit_message_text("Permintaan kamu sedang diproses.. ")
            try:
                url = f"https://www.imdb.com/title/{movie}/"
                resp = await get_content(url)
                sop = BeautifulSoup(resp, "lxml")
                r_json = json.loads(
                    sop.find("script", attrs={
                        "type": "application/ld+json"
                    }).contents[0])
                res_str = ""
                type = f"<code>{r_json['@type']}</code>" if r_json.get(
                    "@type") else ""
                if r_json.get("name"):
                    try:
                        tahun = sop.select('ul[data-testid="hero-title-block__metadata"]')[0].find(class_="sc-8c396aa2-2 itZqyK").text
                    except:
                        tahun = "-"
                    res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json['name']} [{tahun}]</a> (<code>{type}</code>)\n"
                if r_json.get("alternateName"):
                    res_str += f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
                else:
                    res_str += "\n"
                if sop.select('li[data-testid="title-techspec_runtime"]'):
                    durasi = sop.select('li[data-testid="title-techspec_runtime"]')[0].find(class_="ipc-metadata-list-item__content-container").text
                    res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
                if r_json.get("contentRating"):
                    res_str += f"<b>Kategori:</b> <code>{r_json['contentRating']}</code> \n"
                if r_json.get("aggregateRating"):
                    res_str += f"<b>Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
                if sop.select('li[data-testid="title-details-releasedate"]'):
                    rilis = sop.select('li[data-testid="title-details-releasedate"]')[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
                    rilis_url = sop.select('li[data-testid="title-details-releasedate"]')[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")['href']
                    res_str += f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
                if r_json.get("genre"):
                    genre = ""
                    for i in r_json['genre']:
                        if i == "Comedy":
                            genre += f"🤣 #{i}, "
                        elif i == "Family":
                            genre += f"👨‍👩‍👧‍👧 #{i}, "
                        elif i == "Drama":
                            genre += f"🎭 #{i}, "
                        elif i == "Musical":
                            genre += f"🎸 #{i}, "
                        elif i == "Adventure":
                            genre += f"🌋 #{i}, "
                        elif i == "Sci_Fi":
                            genre += f"🤖 #{i}, "
                        elif i == "Fantasy":
                            genre += f"✨ #{i}, "
                        elif i == "Horror":
                            genre += f"👻 #{i}, "
                        elif i == "Romance":
                            genre += f"🌹 #{i}, "
                        else:
                            genre += f"#{i}, "
                    genre = genre[:-2].replace("-", "_")
                    res_str += f"<b>Genre:</b> {genre}\n"
                if sop.select('li[data-testid="title-details-origin"]'):
                    country = "".join(f"{demoji(country.text)} #{country.text.replace(' ', '_')}, " for country in sop.select('li[data-testid="title-details-origin"]')[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
                    country = country[:-2]
                    res_str += f"<b>Negara:</b> {country}\n"
                if sop.select('li[data-testid="title-details-languages"]'):
                    language = "".join(f"#{lang.text.replace(' ', '_')}, " for lang in sop.select('li[data-testid="title-details-languages"]')[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
                    language = language[:-2]
                    res_str += f"<b>Bahasa:</b> {language}\n"
                res_str += "\n<b>🙎 Info Cast:</b>\n"
                if r_json.get("director"):
                    director = ""
                    for i in r_json['director']:
                        name = i['name']
                        url = i['url']
                        director +=  f"<a href='https://www.imdb.com{url}'>{name}</a>, "
                    director = director[:-2]
                    res_str += f"<b>Sutradara:</b> {director}\n"
                if r_json.get("creator"):
                    creator = ""
                    for i in r_json['creator']:
                        if i['@type'] == 'Person':
                            name = i['name']
                            url = i['url']
                            creator +=  f"<a href='https://www.imdb.com{url}'>{name}</a>, "
                    creator = creator[:-2]
                    res_str += f"<b>Penulis:</b> {creator}\n"
                if r_json.get("actor"):
                    actors = ""
                    for i in r_json['actor']:
                        name = i['name']
                        url = i['url']
                        actors +=  f"<a href='https://www.imdb.com{url}'>{name}</a>, "
                    actors = actors[:-2]
                    res_str += f"<b>Pemeran:</b> {actors}\n\n"
                if r_json.get("description"):
                    summary = GoogleTranslator('auto', 'id').translate(r_json.get('description'))
                    res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
                if r_json.get("keywords"):
                    keywords = r_json["keywords"].split(",")
                    key_ = ""
                    for i in keywords:
                        i = i.replace(" ", "_")
                        key_ += f"#{i}, "
                    key_ = key_[:-2]
                    res_str += f"<b>🔥 Kata Kunci:</b> {key_} \n"
                if sop.select('li[data-testid="award_information"]'):
                    awards = sop.select('li[data-testid="award_information"]')[0].find(class_="ipc-metadata-list-item__list-content-item").text
                    res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(awards)}</code>\n\n"
                else:
                    res_str += "\n"
                res_str += "<b>©️ IMDb by</b> @MissKatyRoBot"
                if r_json.get("trailer"):
                    trailer_url = r_json["trailer"]["url"]
                    markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            "🎬 Open IMDB",
                            url=f"https://www.imdb.com{r_json['url']}"),
                        InlineKeyboardButton("▶️ Trailer", url=trailer_url)
                    ]])
                else:
                    markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            "🎬 Open IMDB",
                            url=f"https://www.imdb.com{r_json['url']}")
                    ]])
                await query.edit_message_caption(res_str, reply_markup=markup, disable_web_page_preview=False)
            except Exception:
                exc = traceback.format_exc()
                await query.edit_message_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")
        else:
            await query.answer("⚠️ Akses Ditolak!", True)                
