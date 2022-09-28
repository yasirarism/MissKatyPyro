import json, traceback
from bot import app
from bot.plugins.other_tools import get_content
from bot.helper.http import http
from pyrogram import filters, enums
from bs4 import BeautifulSoup
from gpytranslate import Translator
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

__MODULE__ = "InlineFeature"
__HELP__ = """
To use this feature, just type bot username with following args below.
~ imdb [query] - Search movie details in IMDb.com.
~ pypi [query] - Search package from Pypi.
~ git [query] - Search in Git.
~ google [query] - Search in Google.
"""


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
        f"https://betterimdbot.herokuapp.com/search.php?_={movie_name}")
    srch_results = json.loads(search_results.text)
    asroe = srch_results.get("d")
    oorse = []
    for sraeo in asroe:
        title = sraeo.get("l", "")
        description = sraeo.get("q", "")
        stars = sraeo.get("s", "")
        imdb_url = f"https://imdb.com/title/{sraeo.get('id')}"
        year = sraeo.get("yr", "").rstrip("-")
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
                        f"imdbinl#{inline_query.from_user.id}#{sraeo.get('id')}"
                    )
                ]]),
            ))
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
        f"https://kamiselaluada.me/api/pypi?package={query}")
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


@app.on_callback_query(filters.regex("^imdbinl#"))
async def imdb_inl(_, query):
        i, user, movie = query.data.split("#")
        if query.from_user.id != user:
            return await query.answer("⚠️ Akses Ditolak!", True)
        await query.message.edit_text("Permintaan kamu sedang diproses.. ")
        try:
            trl = Translator()
            url = f"https://www.imdb.com/title/tt{movie}/"
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
                res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json['name']}</a> (<code>{type}</code>)\n"
            if r_json.get("alternateName"):
                res_str += f"<b>📢 AKA:</b> <code>{r_json['alternateName']}</code>\n\n"
            else:
                res_str += "\n"
            if sop.select('li[data-testid="title-techspec_runtime"]'):
                durasi = sop.select('li[data-testid="title-techspec_runtime"]')[0].find(class_="ipc-metadata-list-item__content-container").text
                res_str += f"<b>🕓 Durasi:</b> <code>{(await trl(durasi, targetlang='id')).text}</code>\n"
            if r_json.get("contentRating"):
                res_str += f"<b>🔞 Kategori:</b> <code>{r_json['contentRating']}</code> \n"
            if r_json.get("aggregateRating"):
                res_str += f"<b>🏆 Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']} dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
            if sop.select('li[data-testid="title-details-releasedate"]'):
                rilis = sop.select('li[data-testid="title-details-releasedate"]')[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
                res_str += f"<b>📆 Rilis:</b> <code>{rilis}</code>\n"
            if r_json.get("genre"):
                all_genre = r_json["genre"]
                genre = "".join(f"#{i}, " for i in all_genre)
                genre = genre[:-2].replace("-", "_")
                res_str += f"<b>🎭 Genre:</b> {genre}\n"
            if sop.select('li[data-testid="title-details-origin"]'):
                country = "".join(f"{country.text}, " for country in sop.select('li[data-testid="title-details-origin"]')[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
                country = country[:-2]
                res_str += f"<b>🆔 Negara:</b> <code>{country}</code>\n"
            if sop.select('li[data-testid="title-details-languages"]'):
                language = "".join(f"{lang.text}, " for lang in sop.select('li[data-testid="title-details-languages"]')[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"))
                language = language[:-2]
                res_str += f"<b>🔊 Bahasa:</b> <code>{language}</code>\n"
            if r_json.get("director"):
                all_director = r_json["director"]
                director = "".join(f"{i['name']}, " for i in all_director)
                director = director[:-2]
                res_str += f"<b>Sutradara:</b> <code>{director}</code>\n"
            if r_json.get("actor"):
                all_actors = r_json["actor"]
                actors = "".join(f"{i['name']}, " for i in all_actors)
                actors = actors[:-2]
                res_str += f"<b>Pemeran:</b> <code>{actors}</code>\n\n"
            if r_json.get("description"):
                summary = await trl(r_json["description"].replace("  ", " "),
                                    targetlang="id")
                res_str += f"<b>📜 Plot: </b> <code>{summary.text}</code>\n\n"
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
                res_str += f"<b>🏆 Penghargaan:</b> <code>{(await trl(awards, targetlang='id')).text}</code>\n\n"
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
            if thumb := r_json.get("image"):
                try:
                    await query.message.reply_photo(
                        photo=thumb,
                        quote=True,
                        caption=res_str,
                        reply_to_message_id=usr.id,
                        reply_markup=markup)
                except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                    poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                    await query.message.reply_photo(
                        photo=poster,
                        caption=res_str,
                        reply_to_message_id=usr.id,
                        reply_markup=markup)
                except Exception:
                    await query.message.reply(res_str,
                                              reply_markup=markup,
                                              disable_web_page_preview=False,
                                              reply_to_message_id=usr.id)
                await query.message.delete()
            else:
                await query.message.edit(res_str,
                                         reply_markup=markup,
                                         disable_web_page_preview=False)
            await query.answer()
        except Exception:
            exc = traceback.format_exc()
            await query.message.edit_text(f"<b>ERROR:</b>\n<code>{exc}</code>")