# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import html
import json
import re
import traceback
from logging import getLogger
from sys import platform
from sys import version as pyver

from bs4 import BeautifulSoup
from pykeyboard import InlineButton, InlineKeyboard
from pyrogram import __version__ as pyrover
from pyrogram import enums, filters
from pyrogram.errors import MessageIdInvalid, MessageNotModified
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

from database.imdb_db import get_imdb_by, get_imdb_layout_fields, get_imdb_template
from misskaty import BOT_USERNAME, app, user
from misskaty.helper import GENRES_EMOJI, fetch, gtranslate, post_to_telegraph, search_jw
from misskaty.plugins.dev import shell_exec
from misskaty.plugins.misc_tools import calc_btn
from misskaty.vars import USER_SESSION
from utils import demoji

__MODULE__ = "InlineFeature"
__HELP__ = """
To use this feature, just type bot username with following args below.
~ imdb [query] - Search movie details in IMDb.com.
~ pypi [query] - Search package from Pypi.
~ git [query] - Search in Git.
~ google [query] - Search in Google.
~ info [user id/username] - Check info about a user.
"""

keywords_list = ["imdb", "pypi", "git", "google", "secretmsg", "info", "botapi"]

PRVT_MSGS = {}
LOGGER = getLogger("MissKaty")


class _ImdbTemplateDefaults(dict):
    def __missing__(self, key):
        return "-"


def _render_template_buttons(template: str, payload: dict):
    buttons = []

    def _replace(match: re.Match) -> str:
        label = match.group(1)
        url = match.group(2)
        try:
            label = label.format_map(_ImdbTemplateDefaults(payload))
            url = url.format_map(_ImdbTemplateDefaults(payload))
        except Exception:
            return ""
        if url.startswith("http"):
            buttons.append(InlineKeyboardButton(label, url=url))
        return ""

    template_without_buttons = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)", _replace, template
    )
    return template_without_buttons, buttons


def render_imdb_template(template: str, payload: dict) -> str | None:
    try:
        normalized = template.replace("\\n", "\n")
        rendered = normalized.format_map(_ImdbTemplateDefaults(payload))
        return re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<a href=\"\2\">\1</a>", rendered
        )
    except Exception as err:
        LOGGER.warning(f"Failed rendering IMDB template: {err}")
        return None


def render_imdb_template_with_buttons(template: str, payload: dict):
    try:
        normalized = template.replace("\\n", "\n")
        template_without_buttons, buttons = _render_template_buttons(
            normalized, payload
        )
        rendered = template_without_buttons.format_map(_ImdbTemplateDefaults(payload))
        return rendered, buttons
    except Exception as err:
        LOGGER.warning(f"Failed rendering IMDB template with buttons: {err}")
        return None, []


def _with_html_placeholders(payload: dict) -> dict:
    enriched = dict(payload)
    for key, value in payload.items():
        if value is None:
            value = "-"
        if isinstance(value, str):
            enriched[f"{key}_html"] = html.escape(value)
    return enriched


@app.on_inline_query()
async def inline_menu(self, inline_query: InlineQuery):
    if inline_query.query.strip().lower().strip() == "":
        aspymon_ver = (await shell_exec("pip freeze | grep async-pymongo"))[0]
        buttons = InlineKeyboard(row_width=2)
        buttons.add(
            *[
                (InlineKeyboardButton(text=i, switch_inline_query_current_chat=i))
                for i in keywords_list
            ]
        )

        btn = InlineKeyboard(row_width=2)
        bot_state = "Alive" if USER_SESSION and await app.get_me() else "Dead"
        ubot_state = "Alive" if USER_SESSION and await user.get_me() else "Dead"
        btn.add(
            InlineKeyboardButton("Stats", callback_data="stats_callback"),
            InlineKeyboardButton("Go Inline!", switch_inline_query_current_chat=""),
        )

        msg = f"""
**[MissKaty✨](https://github.com/yasirarism):**
**MainBot Stats:** `{bot_state}`
**UserBot Stats:** `{ubot_state}`
**Python:** `{pyver.split()[0]}`
**Pyrogram:** `{pyrover}`
**MongoDB:** `{aspymon_ver}`
**Platform:** `{platform}`
**Bot:** {(await app.get_me()).first_name}
"""
        if USER_SESSION:
            msg += f"**UserBot:** {(await user.get_me()).first_name}"
        answerss = [
            InlineQueryResultArticle(
                title="Inline Commands",
                description="Help Related To Inline Usage.",
                input_message_content=InputTextMessageContent(
                    "Click A Button To Get Started."
                ),
                thumb_url="https://hamker.me/cy00x5x.png",
                reply_markup=buttons,
            ),
            InlineQueryResultArticle(
                title="Github Repo",
                description="Github Repo of This Bot.",
                input_message_content=InputTextMessageContent(
                    f"<b>Github Repo @{BOT_USERNAME}</b>\n\nhttps://github.com/yasirarism/MissKatyPyro"
                ),
                thumb_url="https://hamker.me/gjc9fo3.png",
            ),
            InlineQueryResultArticle(
                title="Alive",
                description="Check Bot's Stats",
                thumb_url="https://yt3.ggpht.com/ytc/AMLnZu-zbtIsllERaGYY8Aecww3uWUASPMjLUUEt7ecu=s900-c-k-c0x00ffffff-no-rj",
                input_message_content=InputTextMessageContent(
                    msg, disable_web_page_preview=True
                ),
                reply_markup=btn,
            ),
        ]
        await inline_query.answer(results=answerss)
    elif inline_query.query.strip().lower().split()[0] == "calc":
        if len(inline_query.query.strip().lower().split()) < 2:
            answers = [
                InlineQueryResultArticle(
                    title="Calculator",
                    description="New Calculator",
                    input_message_content=InputTextMessageContent(
                        message_text=f"Made by @{self.me.username}",
                        disable_web_page_preview=True,
                    ),
                    reply_markup=calc_btn(inline_query.from_user.id),
                )
            ]
        else:
            data = inline_query.query.replace("×", "*").replace("÷", "/")
            result = str(eval(text))
            answers = [
                InlineQueryResultArticle(
                    title="Answer",
                    description=f"Result: {result}",
                    input_message_content=InputTextMessageContent(
                        message_text=f"{data} = {result}", disable_web_page_preview=True
                    ),
                )
            ]
        await inline_query.answer(
            results=answers,
            is_gallery=False,
            is_personal=False,
            switch_pm_parameter="help",
        )
    elif inline_query.query.strip().lower().split()[0] == "botapi":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Bot Api Docs | botapi [QUERY]",
                switch_pm_parameter="inline",
            )
        kueri = inline_query.query.split(None, 1)[1].strip()
        jsonapi = await fetch.get(
            "https://github.com/PaulSonOfLars/telegram-bot-api-spec/raw/main/api.json",
            follow_redirects=True,
        )
        parsemethod = jsonapi.json().get("methods")
        parsetypes = jsonapi.json().get("types")
        datajson = []
        method = None
        is_img = False
        for method in parsemethod:
            if kueri.lower() in method.lower():
                link = parsemethod[method]["href"]
                description = parsemethod[method]["description"][0]
                buttons = InlineKeyboard()
                buttons.row(
                    InlineButton("Open Docs", url=link),
                    InlineButton(
                        "Search Again",
                        switch_inline_query_current_chat=inline_query.query,
                    ),
                )
                buttons.row(
                    InlineButton("Give Coffee", url="https://yasirpedia.eu.org"),
                )
                returns = "".join(f"{i}, " for i in parsemethod[method]["returns"])
                msg = f"<b>{method}</b> (<code>{returns[:-2]}</code>)\n"
                msg += f"{description}\n\n"
                msg += "<b>Variables:</b>\n"
                if parsemethod[method].get("fields"):
                    for i in parsemethod[method]["fields"]:
                        msg += f"<code>{i['name']}</code> (<b>{i['types'][0]}</b>)\n<b>Required:</b> <code>{i['required']}</code>\n{i['description']}\n\n"
                if len(msg.encode("utf-8")) > 4096:
                    body_text = f"""
                        <pre>{msg.replace("<user_id>", "(user_id)")}</pre>
                        """
                    msg = await post_to_telegraph(is_img, method, body_text)
                datajson.append(
                    InlineQueryResultArticle(
                        title=method,
                        input_message_content=InputTextMessageContent(
                            message_text=msg,
                            parse_mode=enums.ParseMode.HTML,
                            disable_web_page_preview=True,
                        ),
                        url=link,
                        description=description,
                        thumb_url="https://img.freepik.com/premium-vector/open-folder-folder-with-documents-document-protection-concept_183665-104.jpg",
                        reply_markup=buttons,
                    )
                )
        for types in parsetypes:
            if kueri.lower() in types.lower():
                link = parsetypes[types]["href"]
                description = parsetypes[types]["description"][0]
                buttons = InlineKeyboard()
                buttons.row(
                    InlineButton("Open Docs", url=link),
                    InlineButton(
                        "Search Again",
                        switch_inline_query_current_chat=inline_query.query,
                    ),
                )
                buttons.row(
                    InlineButton("Give Coffee", url="https://yasirpedia.eu.org"),
                )
                msg = f"<b>{types}</b>\n"
                msg += f"{description}\n\n"
                msg += "<b>Variables:</b>\n"
                if parsetypes[types].get("fields"):
                    for i in parsetypes[types]["fields"]:
                        msg += f"<code>{i['name']}</code> (<b>{i['types'][0]}</b>)\n<b>Required:</b> <code>{i['required']}</code>\n{i['description']}\n\n"
                if len(msg.encode("utf-8")) > 4096:
                    body_text = f"""
                        <pre>{msg}</pre>
                        """
                    msg = await post_to_telegraph(is_img, method, body_text)
                datajson.append(
                    InlineQueryResultArticle(
                        title=types,
                        input_message_content=InputTextMessageContent(
                            message_text=msg,
                            parse_mode=enums.ParseMode.HTML,
                            disable_web_page_preview=True,
                        ),
                        url=link,
                        description=description,
                        thumb_url="https://img.freepik.com/premium-vector/open-folder-folder-with-documents-document-protection-concept_183665-104.jpg",
                        reply_markup=buttons,
                    )
                )
        await inline_query.answer(
            results=datajson[:50],
            is_gallery=False,
            is_personal=False,
            next_offset="",
            cache_time=5,
            switch_pm_text=f"Found {len(datajson)} results",
            switch_pm_parameter="help",
        )
    elif inline_query.query.strip().lower().split()[0] == "google":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Google Search | google [QUERY]",
                switch_pm_parameter="inline",
            )
        judul = inline_query.query.split(None, 1)[1].strip()
        search_results = await fetch.get(
            f"https://www.google.com/search?q={judul}&num=20"
        )
        soup = BeautifulSoup(search_results.text, "lxml")
        data = []
        for result in soup.select(".tF2Cxc"):
            link = result.select_one(".yuRUbf a")["href"]
            title = result.select_one(".DKV0Md").text
            if snippet := result.find(class_="VwiC3b yXK7lf lVm3ye r025kc hJNv6b"):
                snippet = snippet.get_text()
            elif snippet := result.find(class_="VwiC3b yXK7lf lVm3ye r025kc hJNv6b Hdw6tb"):
                snippet = snippet.get_text()
            else:
                snippet = "-"
            message_text = f"<a href='{link}'>{html.escape(title)}</a>\n"
            message_text += f"Deskription: {html.escape(snippet)}\n\nGoogleSearch by @{self.me.username}"
            data.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=snippet,
                    thumb_url="https://te.legra.ph/file/ed8ea62ae636793000bb4.jpg",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Open Website", url=link)]]
                    ),
                )
            )
        await inline_query.answer(
            results=data,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(data)} results",
            switch_pm_parameter="google",
        )
    elif inline_query.query.strip().lower().split()[0] == "info":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="User Info | info [id/username]",
                switch_pm_parameter="inline",
            )
        userr = inline_query.query.split(None, 1)[1].strip()
        if "t.me" in userr:
            r = re.search(r"t.me/(\w+)", userr)
            userr = r[1]
        try:
            diaa = await app.get_users(userr)
        except Exception:  # pylint: disable=broad-except
            inline_query.stop_propagation()
            return
        namanya = (
            f"{diaa.first_name} {diaa.last_name}" if diaa.last_name else diaa.first_name
        )
        msg = f"<b>🏷 Name:</b> {namanya}\n<b>🆔 ID:</b> <code>{diaa.id}</code>\n"
        if diaa.username:
            msg += f"<b>🌐 Username:</b> <code>@{diaa.username}</code>\n"
        if diaa.status:
            msg += f"<b>🕰 User Status:</b> {diaa.status}\n"
        if diaa.dc_id:
            msg += f"<b>🌏 DC:</b> {diaa.dc_id}\n"
        msg += f"<b>✨ Premium:</b> {diaa.is_premium}\n"
        msg += f"<b>⭐️ Verified:</b> {diaa.is_verified}\n"
        msg += f"<b>🤖 Bot:</b> {diaa.is_bot}\n"
        if diaa.language_code:
            msg += f"<b>🇮🇩 Language:</b> {diaa.language_code}"
        results = [
            InlineQueryResultArticle(
                title=f"Get information off {diaa.id}",
                input_message_content=InputTextMessageContent(msg),
                description=f"Get information off {diaa.id}",
            )
        ]
        await inline_query.answer(results=results, cache_time=3)
    elif inline_query.query.strip().lower().split()[0] == "secretmsg":
        if len(inline_query.query.strip().lower().split()) < 3:
            return await inline_query.answer(
                results=[],
                switch_pm_text="SecretMsg | secretmsg [USERNAME/ID] [MESSAGE]",
                switch_pm_parameter="inline",
            )
        _id = inline_query.query.split()[1]
        msg = inline_query.query.split(None, 2)[2].strip()

        if not msg or not msg.endswith(":"):
            inline_query.stop_propagation()

        try:
            penerima = await app.get_users(_id.strip())
        except Exception:  # pylint: disable=broad-except
            inline_query.stop_propagation()
            return

        PRVT_MSGS[inline_query.id] = (
            penerima.id,
            penerima.first_name,
            inline_query.from_user.id,
            msg.strip(": "),
        )
        prvte_msg = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Show Message 🔐", callback_data=f"prvtmsg({inline_query.id})"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Destroy☠️ this msg",
                        callback_data=f"destroy({inline_query.id})",
                    )
                ],
            ]
        )
        mention = (
            f"@{penerima.username}"
            if penerima.username
            else f"<a href='tg://user?id={penerima.id}'>{penerima.first_name}</a>"
        )
        msg_c = (
            f"🔒 A <b>private message</b> to {mention} [<code>{penerima.id}</code>], "
        )
        msg_c += "Only he/she can open it."
        results = [
            InlineQueryResultArticle(
                title=f"A Private Msg to {penerima.first_name}",
                input_message_content=InputTextMessageContent(msg_c),
                description="Only he/she can open it",
                thumb_url="https://te.legra.ph/file/16133ab3297b3f73c8da5.png",
                reply_markup=prvte_msg,
            )
        ]
        await inline_query.answer(results=results, cache_time=3)
    elif inline_query.query.strip().lower().split()[0] == "git":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Github Search | git [QUERY]",
                switch_pm_parameter="inline",
            )
        query = inline_query.query.split(None, 1)[1].strip()
        search_results = await fetch.get(
            f"https://api.github.com/search/repositories?q={query}"
        )
        srch_results = json.loads(search_results.text)
        item = srch_results.get("items")
        data = []
        for result in item:
            title = result.get("full_name")
            link = result.get("html_url")
            desc = result.get("description") if result.get("description") else ""
            deskripsi = desc[:100] if len(desc) > 100 else desc
            lang = result.get("language")
            message_text = f"🔗: {result.get('html_url')}\n│\n└─🍴Forks: {result.get('forks')}    ┃┃    🌟Stars: {result.get('stargazers_count')}\n\n"
            message_text += f"<b>Description:</b> {deskripsi}\n"
            message_text += f"<b>Language:</b> {lang}"
            data.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=deskripsi,
                    thumb_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Open Github Link", url=link)]]
                    ),
                )
            )
        await inline_query.answer(
            results=data,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(data)} results",
            switch_pm_parameter="github",
        )
    elif inline_query.query.strip().lower().split()[0] == "pypi":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Pypi Search | pypi [QUERY]",
                switch_pm_parameter="inline",
            )
        query = inline_query.query.split(None, 1)[1].strip()
        search_results = await fetch.get(f"https://yasirapi.eu.org/pypi?q={query}")
        srch_results = search_results.json()
        data = []
        for sraeo in srch_results["result"]:
            title = sraeo.get("name")
            link = sraeo.get("url")
            deskripsi = sraeo.get("description")
            version = sraeo.get("version")
            message_text = f"<a href='{link}'>{title} {version}</a>\n"
            message_text += f"Description: {deskripsi}\n"
            data.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=deskripsi,
                    thumb_url="https://raw.githubusercontent.com/github/explore/666de02829613e0244e9441b114edb85781e972c/topics/pip/pip.png",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Open Link", url=link)]]
                    ),
                )
            )
        await inline_query.answer(
            results=data,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(data)} results",
            switch_pm_parameter="pypi",
        )
    elif inline_query.query.strip().lower().split()[0] == "yt":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="YouTube Search | yt [QUERY]",
                switch_pm_parameter="inline",
            )
        judul = inline_query.query.split(None, 1)[1].strip()
        search_results = await fetch.get(
            f"https://api.abir-hasan.tk/youtube?query={judul}"
        )
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
                deskripsi = "".join(
                    f"{i['text']} " for i in sraeo.get("descriptionSnippet")
                )
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
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=deskripsi,
                    thumb_url=thumb,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Watch Video 📹", url=link)]]
                    ),
                )
            )
        await inline_query.answer(
            results=oorse,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(asroe)} results",
            switch_pm_parameter="yt",
        )
    elif inline_query.query.strip().lower().split()[0] == "imdb":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="IMDB Search | imdb [QUERY]",
                switch_pm_parameter="inline",
            )
        movie_name = inline_query.query.split(None, 1)[1].strip()
        search_results = await fetch.get(
            f"https://yasirapi.eu.org/imdb-search?q={movie_name}"
        )
        imdb_payload = json.loads(search_results.text)
        res = imdb_payload.get("result")
        if isinstance(res, str):
            try:
                res = json.loads(res)
            except json.JSONDecodeError:
                res = []
        if isinstance(res, dict):
            res = res.get("d") or res.get("results") or []
        if not isinstance(res, list):
            res = []
        hidden_fields = set(await get_imdb_layout_fields(inline_query.from_user.id) or [])
        disable_web_preview = "web_preview" in hidden_fields
        send_as_photo = "send_as_photo" not in hidden_fields
        oorse = []
        for midb in res:
            if not isinstance(midb, dict):
                continue
            title = midb.get("l", "")
            description = midb.get("q", "")
            stars = midb.get("s", "")
            imdb_id = midb.get("id", "")
            imdb_url = f"https://imdb.com/title/{imdb_id}"
            year = f"({midb.get('y', '')})"
            image = midb.get("i")
            image_url = "https://te.legra.ph/file/e263d10ff4f4426a7c664.jpg"
            if isinstance(image, dict):
                image_url = image.get("imageUrl", image_url)
            elif isinstance(image, str) and image:
                image_url = image
            if image_url.endswith(".jpg"):
                image_url = image_url.replace(".jpg", "._V1_UX360.jpg")
            caption = f"<a href='{image_url}'>🎬</a>"
            caption += f"<a href='{imdb_url}'>{title} {year}</a>"
            description_text = f" {description} | {stars}"
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Get IMDB details",
                            callback_data=f"imdbinl#{inline_query.from_user.id}#{imdb_id}",
                        )
                    ]
                ]
            )
            if send_as_photo:
                oorse.append(
                    InlineQueryResultPhoto(
                        title=f"{title} {year}",
                        caption=caption,
                        description=description_text,
                        photo_url=image_url,
                        reply_markup=reply_markup,
                    )
                )
            else:
                message_text = f"{caption}\n{description_text}"
                oorse.append(
                    InlineQueryResultArticle(
                        title=f"{title} {year}",
                        description=description_text,
                        thumb_url=image_url,
                        url=imdb_url if not disable_web_preview else None,
                        reply_markup=reply_markup,
                        input_message_content=InputTextMessageContent(
                            message_text=message_text,
                            parse_mode=enums.ParseMode.HTML,
                            disable_web_page_preview=disable_web_preview,
                        ),
                    )
                )
        resfo = imdb_payload.get("q")
        await inline_query.answer(
            results=oorse,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(oorse)} results for {resfo}",
            switch_pm_parameter="imdb",
        )


@app.on_callback_query(filters.regex(r"prvtmsg\((.+)\)"))
async def prvt_msg(_, c_q):
    msg_id = str(c_q.matches[0].group(1))

    if msg_id not in PRVT_MSGS:
        await c_q.answer("Message now outdated !", show_alert=True)
        return

    user_id, flname, sender_id, msg = PRVT_MSGS[msg_id]

    if c_q.from_user.id in (user_id, sender_id):
        await c_q.answer(msg, show_alert=True)
    else:
        await c_q.answer(f"Only {flname} can see this Private Msg!", show_alert=True)


@app.on_callback_query(filters.regex(r"destroy\((.+)\)"))
async def destroy_msg(_, c_q):
    msg_id = str(c_q.matches[0].group(1))

    if msg_id not in PRVT_MSGS:
        await c_q.answer("message now outdated !", show_alert=True)
        return

    user_id, flname, sender_id, _ = PRVT_MSGS[msg_id]

    if c_q.from_user.id in (user_id, sender_id):
        del PRVT_MSGS[msg_id]
        by = "receiver" if c_q.from_user.id == user_id else "sender"
        await c_q.edit_message_text(f"This secret message is ☠️destroyed☠️ by msg {by}")
    else:
        await c_q.answer(f"only {flname} can see this Private Msg!", show_alert=True)


@app.on_callback_query(filters.regex("^imdbinl#"))
async def imdb_inl(_, query):
    i, cbuser, movie = query.data.split("#")
    if cbuser == f"{query.from_user.id}":
        try:
            hidden_fields = set(await get_imdb_layout_fields(query.from_user.id) or [])
            disable_web_preview = "web_preview" in hidden_fields
            send_as_photo = "send_as_photo" not in hidden_fields
            if send_as_photo:
                await query.edit_message_caption(
                    "⏳ <i>Permintaan kamu sedang diproses.. </i>"
                )
            else:
                await query.message.edit_text(
                    "⏳ <i>Permintaan kamu sedang diproses.. </i>",
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            url = f"https://www.imdb.com/title/{movie}/"
            resp = await fetch.get(url)
            sop = BeautifulSoup(resp, "lxml")
            r_json = json.loads(
                sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
            )
            ott = await search_jw(r_json.get("alternateName") or r_json["name"], "ID")
            template = await get_imdb_template(query.from_user.id)
            imdb_by = await get_imdb_by(query.from_user.id) or f"@{app.me.username}"
            res_str = ""
            typee = r_json.get("@type", "")
            duration_text = "-"
            duration_raw = "-"
            category_text = "-"
            release_date_text = "-"
            genre_text = "-"
            country_text = "-"
            language_text = "-"
            director_text = "-"
            writer_text = "-"
            cast_text = "-"
            storyline_text = "-"
            keyword_text = "-"
            awards_text = "-"
            rilis = "-"
            rilis_url = ""
            summary = ""
            tahun = (
                re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0]
                if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)
                else "N/A"
            )
            res_str += f"<b>📹 Judul:</b> <a href=\"{url}\">{r_json['name']} [{tahun}]</a> (<code>{typee}</code>)\n"
            if r_json.get("alternateName"):
                res_str += (
                    f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
                )
            else:
                res_str += "\n"
            if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
                durasi = (
                    durasi[0]
                    .find(class_="ipc-metadata-list-item__content-container")
                    .text
                )
                duration_raw = durasi
                duration_text = (await gtranslate(durasi, "auto", "id")).text
                res_str += f"<b>Durasi:</b> <code>{duration_text}</code>\n"
            if r_json.get("contentRating"):
                category_text = r_json["contentRating"] or "-"
                res_str += f"<b>Kategori:</b> <code>{r_json['contentRating']}</code> \n"
            if r_json.get("aggregateRating"):
                res_str += f"<b>Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
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
                release_date_text = rilis or "-"
                res_str += f"<b>Rilis:</b> <a href=\"https://www.imdb.com{rilis_url}\">{rilis}</a>\n"
            genre_list = []
            if r_json.get("genre"):
                genre_list = (
                    r_json["genre"]
                    if isinstance(r_json["genre"], list)
                    else [r_json["genre"]]
                )
                genre_text = "".join(
                    f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
                    if i in GENRES_EMOJI
                    else f"#{i.replace('-', '_').replace(' ', '_')}, "
                    for i in genre_list
                )
                res_str += f"<b>Genre:</b> {genre_text[:-2]}\n"
            if genre_text == "-":
                genre_text = "-"
            else:
                genre_text = genre_text[:-2]
            country_list = []
            if negara := sop.select('li[data-testid="title-details-origin"]'):
                country_items = negara[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
                country_list = [country.text for country in country_items]
                country_text = "".join(
                    f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, "
                    for country in country_items
                )
                res_str += f"<b>Negara:</b> {country_text[:-2]}\n"
            if country_text == "-":
                country_text = "-"
            else:
                country_text = country_text[:-2]
            language_list = []
            if bahasa := sop.select('li[data-testid="title-details-languages"]'):
                language_items = bahasa[0].findAll(
                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"
                )
                language_list = [lang.text for lang in language_items]
                language_text = "".join(
                    f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                    for lang in language_items
                )
                res_str += f"<b>Bahasa:</b> {language_text[:-2]}\n"
            if language_text == "-":
                language_text = "-"
            else:
                language_text = language_text[:-2]
            res_str += "\n<b>🙎 Info Cast:</b>\n"
            director_names = []
            if r_json.get("director"):
                director_names = [item["name"] for item in r_json["director"]]
                director = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, "
                    for i in r_json["director"]
                )
                director_text = director[:-2] if director else "-"
                res_str += f"<b>Sutradara:</b> {director[:-2]}\n"
            writer_names = []
            if r_json.get("creator"):
                writer_names = [
                    i["name"] for i in r_json["creator"] if i["@type"] == "Person"
                ]
                creator = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, "
                    for i in r_json["creator"]
                    if i["@type"] == "Person"
                )
                writer_text = creator[:-2] if creator else "-"
                res_str += f"<b>Penulis:</b> {creator[:-2]}\n"
            actor_names = []
            if r_json.get("actor"):
                actor_names = [i["name"] for i in r_json["actor"]]
                actors = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, " for i in r_json["actor"]
                )
                cast_text = actors[:-2] if actors else "-"
                res_str += f"<b>Pemeran:</b> {actors[:-2]}\n\n"
            if r_json.get("description"):
                summary = (await gtranslate(r_json.get("description"), "auto", "id")).text
                storyline_text = summary or "-"
                res_str += f"<b>📜 Plot:</b>\n<blockquote expandable><code>{summary}</code></blockquote>\n\n"
            keywords_list = []
            if r_json.get("keywords"):
                keywords_list = [kw.strip() for kw in r_json["keywords"].split(",")]
                keyword_text = "".join(
                    f"#{i.replace(' ', '_').replace('-', '_')}, "
                    for i in keywords_list
                )
                res_str += (
                    f"<b>🔥 Kata Kunci:</b>\n<blockquote expandable>{keyword_text[:-2]}</blockquote>\n"
                )
            if keyword_text != "-":
                keyword_text = keyword_text[:-2]
            if award := sop.select('li[data-testid="award_information"]'):
                awards = (
                    award[0]
                    .find(class_="ipc-metadata-list-item__list-content-item")
                    .text
                )
                awards_text = (await gtranslate(awards, "auto", "id")).text or "-"
                res_str += f"<b>🏆 Penghargaan:</b>\n<blockquote expandable><code>{awards_text}</code></blockquote>\n"
            else:
                res_str += "\n"
            if ott != "":
                res_str += f"Available On:\n{ott}\n"
            if not ott:
                ott = "-"
            res_str += f"<b>©️ IMDb by</b> {imdb_by}"
            if template:
                imdb_code = movie
                title = r_json.get("name") or "-"
                year_text = tahun
                title_with_year = f"{title} [{year_text}]"
                title_link = f"<a href=\"{url}\">{title_with_year}</a>"
                aka_text = r_json.get("alternateName") or "-"
                rating_value = "-"
                rating_count = "-"
                rating_text = "-"
                if rating := r_json.get("aggregateRating"):
                    rating_value = rating.get("ratingValue", "-")
                    rating_count = rating.get("ratingCount", "-")
                    rating_text = f"{rating_value}⭐️ dari {rating_count} pengguna"
                release_url = (
                    f"https://www.imdb.com{rilis_url}" if rilis_url else "-"
                )
                release_link = (
                    f"<a href=\"{release_url}\">{rilis}</a>" if rilis_url else "-"
                )
                poster_url = r_json.get("image") or "-"
                trailer_url = r_json.get("trailer", {}).get("url") or "-"
                payload = {
                    "title": title,
                    "title_with_year": title_with_year,
                    "title_link": title_link,
                    "aka": aka_text,
                    "type": typee or "-",
                    "year": year_text,
                    "duration": duration_text,
                    "duration_raw": duration_raw,
                    "category": category_text,
                    "rating_value": rating_value,
                    "rating_count": rating_count,
                    "rating_text": rating_text,
                    "release": rilis,
                    "release_url": release_url,
                    "release_link": release_link,
                    "genres": genre_text,
                    "genres_list": ", ".join(genre_list) or "-",
                    "countries": country_text,
                    "countries_list": ", ".join(country_list) or "-",
                    "languages": language_text,
                    "languages_list": ", ".join(language_list) or "-",
                    "directors": ", ".join(director_names) or "-",
                    "writers": ", ".join(writer_names) or "-",
                    "cast": ", ".join(actor_names) or "-",
                    "plot": summary or "-",
                    "keywords": keyword_text,
                    "keywords_list": ", ".join(keywords_list) or "-",
                    "awards": awards_text,
                    "availability": ott,
                    "ott": ott,
                    "imdb_by": imdb_by,
                    "imdb_url": url,
                    "trailer_url": trailer_url,
                    "poster_url": poster_url,
                    "imdb_code": imdb_code,
                    "locale": "id",
                    "link": url,
                    "movie_type": typee or "-",
                    "release_date": release_date_text,
                    "genre": genre_text,
                    "country": country_text,
                    "language": language_text,
                    "director": director_text,
                    "writer": writer_text,
                    "cast_info": "\n".join(
                        [
                            f"Sutradara: {director_text}",
                            f"Penulis: {writer_text}",
                            f"Pemeran: {cast_text}",
                        ]
                    ),
                    "storyline": storyline_text,
                    "keyword": keyword_text,
                }
                template_markup = None
                rendered, template_buttons = render_imdb_template_with_buttons(
                    template, _with_html_placeholders(payload)
                )
                if rendered:
                    res_str = rendered
                    if template_buttons:
                        template_markup = InlineKeyboardMarkup([template_buttons])
            else:
                if "title" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>📹 Judul:</b> <a href=\"{url}\">{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n",
                        "",
                    )
                if "release_date" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Rilis:</b> <a href=\"https://www.imdb.com{rilis_url}\">{rilis}</a>\n",
                        "",
                    )
                if "genre" in hidden_fields:
                    res_str = res_str.replace(f"<b>Genre:</b> {genre_text}\n", "")
                if "country" in hidden_fields:
                    res_str = res_str.replace(f"<b>Negara:</b> {country_text}\n", "")
                if "language" in hidden_fields:
                    res_str = res_str.replace(f"<b>Bahasa:</b> {language_text}\n", "")
                if "cast" in hidden_fields:
                    res_str = res_str.replace("\n<b>🙎 Info Cast:</b>\n", "")
                    res_str = res_str.replace(f"<b>Sutradara:</b> {director_text}\n", "")
                    res_str = res_str.replace(f"<b>Penulis:</b> {writer_text}\n", "")
                    res_str = res_str.replace(f"<b>Pemeran:</b> {cast_text}\n\n", "")
                if "storyline" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>📜 Plot:</b>\n<blockquote expandable><code>{summary}</code></blockquote>\n\n",
                        "",
                    )
                if "keyword" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>🔥 Kata Kunci:</b>\n<blockquote expandable>{keyword_text}</blockquote>\n",
                        "",
                    )
                if "awards" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>🏆 Penghargaan:</b>\n<blockquote expandable><code>{awards_text}</code></blockquote>\n",
                        "",
                    )
                if "ott" in hidden_fields:
                    res_str = res_str.replace(f"Available On:\n{ott}\n", "")
                if "imdb_by" in hidden_fields:
                    res_str = res_str.replace(f"<b>©️ IMDb by</b> {imdb_by}", "")
            if template:
                markup = template_markup
            elif r_json.get("trailer"):
                trailer_url = r_json["trailer"]["url"]
                buttons = []
                if "open_imdb" not in hidden_fields:
                    buttons.append(InlineKeyboardButton("🎬 Buka IMDB", url=url))
                if "trailer" not in hidden_fields:
                    buttons.append(InlineKeyboardButton("▶️ Trailer", url=trailer_url))
                markup = InlineKeyboardMarkup([buttons]) if buttons else None
            else:
                if "open_imdb" in hidden_fields:
                    markup = None
                else:
                    markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🎬 Open IMDB",
                                    url=url,
                                )
                            ]
                        ]
                    )
            if send_as_photo:
                await query.edit_message_caption(
                    res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup
                )
            else:
                await query.message.edit_text(
                    res_str,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                    disable_web_page_preview=disable_web_preview,
                )
        except (MessageNotModified, MessageIdInvalid):
            pass
        except Exception:
            exc = traceback.format_exc()
            if send_as_photo:
                await query.edit_message_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")
            else:
                await query.message.edit_text(
                    f"<b>ERROR:</b>\n<code>{exc}</code>",
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True,
                )
    else:
        await query.answer("⚠️ Akses Ditolak!", True)
