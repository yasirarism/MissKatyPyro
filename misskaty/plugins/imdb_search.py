# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
import contextlib
import logging
import re
import sys
import traceback
from urllib.parse import quote_plus

import httpx
from pyrogram import Client, enums
from pyrogram import types as pyro_types
from pyrogram.errors import (
    MediaCaptionTooLong,
    MessageIdInvalid,
    MessageNotModified,
    MessageTooLong,
    PhotoInvalidDimensions,
    QueryIdInvalid,
    WebpageMediaEmpty,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputRichMessage,
    Message,
    ReplyParameters,
)

from database.imdb_db import (
    add_imdbset,
    get_imdb_by,
    get_imdb_layout,
    get_imdb_layout_fields,
    get_imdb_template,
    is_imdbset,
    remove_imdb_by,
    remove_imdb_template,
    remove_imdbset,
    reset_imdb_layout_fields,
    set_imdb_by,
    set_imdb_layout,
    set_imdb_layout_fields,
    set_imdb_template,
)
from misskaty import app
from misskaty.helper import GENRES_EMOJI, Cache, fetch, gtranslate, get_random_string, search_jw
from misskaty.helper.imdb_graphql import format_imdb_date, get_imdb_details_graphql
from misskaty.helper.chat_utils import demoji

LOGGER = logging.getLogger("MissKaty")
LIST_CARI = Cache(filename="imdb_cache.db", path="cache", in_memory=False)

from misskaty.helper.imdb_graphql import format_imdb_awards
from misskaty.helper.imdb_template import (
    _with_html_placeholders,
    format_imdb_money,
    render_imdb_template_with_buttons,
)


def _imdb_settings_caption(name: str):
    return (
        f"Halo {name} | Ready TelePrem, CapCut, Canva, Netflix, dll!\n"
        "Kelola preferensi IMDb Search kamu di sini.\n\n"
        "• 🎛 Edit Layout → pilih informasi apa saja yang tampil di hasil detail.\n"
        "• 🧩 Custom Layout → pakai template HTML sendiri.\n"
        "• 📝 IMDb By → atur nama/username yang muncul di kredit.\n"
        "• 🚩 Language → set bahasa default saat memakai /imdb.\n\n"
        "Sentuh salah satu tombol di bawah untuk memulai."
    )


def _imdb_layout_caption():
    return (
        "<b>Edit Layout IMDb</b>\n"
        "Silahkan edit layout IMDb anda, tekan reset untuk kembali ke default."
    )


def _imdb_settings_keyboard(uid: int):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎛 Edit Layout", callback_data=f"imdblayoutmenu#{uid}"),
                InlineKeyboardButton("📝 IMDb By", callback_data=f"imdby#{uid}"),
            ],
            [
                InlineKeyboardButton(
                    "🧩 Custom Layout", callback_data=f"imdbtemplatemenu#{uid}"
                ),
                InlineKeyboardButton("🚩 Language", callback_data=f"imdbsetlang#{uid}"),
            ],
            [InlineKeyboardButton("Close", callback_data=f"close#{uid}", icon_custom_emoji_id=5985346521103604145, style=enums.ButtonStyle.DANGER)],
        ]
    )


def _layout_fields():
    return [
        ("title", "Title"),
        ("duration", "Duration"),
        ("category", "Category"),
        ("rating", "Rating"),
        ("release_date", "Release"),
        ("genre", "Genre"),
        ("country", "Country"),
        ("language", "Language"),
        ("cast", "Cast"),
        ("storyline", "Storyline"),
        ("keyword", "Keyword"),
        ("awards", "Awards"),
        ("ott", "OTT"),
        ("imdb_by", "IMDb by"),
        ("open_imdb", "Open IMDb"),
        ("trailer", "Trailer"),
        ("send_as_photo", "Send as Photo"),
        ("web_preview", "Link Preview"),
    ]


def _layout_field_label(field_key: str, enabled: bool) -> str:
    return f"{'✅' if enabled else '❌'} {dict(_layout_fields()).get(field_key, field_key)}"


def _layout_keyboard(hidden_fields: set, uid: int):
    rows = []
    row = []
    for index, (key, _) in enumerate(_layout_fields(), start=1):
        enabled = key not in hidden_fields
        row.append(
            InlineKeyboardButton(
                _layout_field_label(key, enabled),
                callback_data=f"imdblayouttoggle#{key}#{uid}",
            )
        )
        if index % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton("🔄 Reset", callback_data=f"imdblayoutreset#{uid}"),
            InlineKeyboardButton("↩️ Back", callback_data=f"imdbset#{uid}"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                "Close",
                callback_data=f"close#{uid}",
                icon_custom_emoji_id=IMDB_CUSTOM_EMOJI["close"],
                style=enums.ButtonStyle.DANGER,
            )
        ]
    )
    return InlineKeyboardMarkup(rows)


async def _get_hidden_layout_fields(user_id: int):
    stored = await get_imdb_layout_fields(user_id)
    return set(stored or [])


async def _toggle_layout_field(user_id: int, field_key: str):
    hidden = await _get_hidden_layout_fields(user_id)
    if field_key in hidden:
        hidden.remove(field_key)
    else:
        hidden.add(field_key)
    await set_imdb_layout_fields(user_id, list(hidden))
    return hidden


def _to_rich_html(text: str) -> str:
    """Konversi caption HTML biasa (parse_mode=HTML) ke HTML rich message.

    Rich message tidak merender ``\\n`` sebagai newline — harus pakai ``<br>``
    atau tag blok. `<blockquote expandable>` juga bukan tag rich yang valid,
    diganti `<details>` + `<summary>` supaya tetap collapsible. Custom emoji
    ``<emoji id=...>`` diubah ke bentuk rich ``<tg-emoji emoji-id=...>``.
    """
    # 0) Custom emoji -> bentuk rich message (terima bentuk quoted & unquoted)
    text = re.sub(
        r'<emoji id="?(\d+)"?>([^<]*)</emoji>',
        r'<tg-emoji emoji-id="\1">\2</tg-emoji>',
        text,
    )
    # 1) Blockquote expandable -> <details><summary>
    text = re.sub(
        r"<blockquote expandable><code>(.*?)</code></blockquote>",
        r"<details><summary>🔍 Detail</summary><code>\1</code></details>",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<blockquote expandable>(.*?)</blockquote>",
        r"<details><summary>🔍 Detail</summary>\1</details>",
        text,
        flags=re.DOTALL,
    )
    # 2) Baris biasa rapat <p>; blank line jadi jarak antar section (collapse
    #    ganda); baris setelah blank (section header) tanpa <p> supaya 1 enter.
    text = text.strip()
    lines = [ln.strip() for ln in text.split("\n")]
    out = []
    prev_blank = False
    for ln in lines:
        if not ln:
            if not prev_blank:
                out.append("<br>")
            prev_blank = True
            continue
        is_header = prev_blank
        prev_blank = False
        if "<details" in ln or ln.startswith(
            ("<blockquote", "<hr", "<h", "<img", "<figure", "<ul", "<ol", "<table")
        ):
            out.append(ln)
        elif is_header:
            out.append(ln)
        else:
            out.append(f"<p>{ln}</p>")
    return "".join(out)


async def _send_rich_result(self, query, res_str, markup, poster_url=None):
    """Kirim hasil IMDb sebagai rich message (caption kepanjangan / user pilih).

    Prioritas sekarang: EDIT pesan yang sudah ada menjadi rich message
    (didukung ``edit_message_text`` + ``rich_message`` di fork Kurigram),
    jadi tidak perlu hapus-lalu-kirim pesan baru. Poster dikirim via
    ``<img src="URL">`` (server Telegram yang fetch URL); kalau gagal ->
    fallback rich tanpa foto, lalu edit HTML biasa. Kirim pesan baru hanya
    dipakai sebagai jalan terakhir kalau pesan asli sudah tidak bisa diedit.
    """
    chat_id = query.message.chat.id
    rich_html = _to_rich_html(res_str)
    photo_html = f'<img src="{poster_url}"/>\n\n' if poster_url else ""
    attempts = [photo_html + rich_html, rich_html] if photo_html else [rich_html]

    for html_content in attempts:
        result = await query.message.edit_rich(
            InputRichMessage(html=html_content), reply_markup=markup
        )
        if result is None:
            # Pesan asli sudah dihapus user -> jalan terakhir: kirim baru
            break
        if result is not False:
            return True

    # Fallback 1: edit HTML biasa (tanpa fitur rich)
    if not poster_url:
        try:
            await query.message.edit(
                res_str,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=markup,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
            )
            return True
        except Exception:
            pass

    # Fallback 2: pesan asli tidak bisa diedit -> kirim rich message baru
    # (tanpa perlu hapus, biarkan user yang hapus pesan lama)
    reply_to = getattr(query.message, "reply_to_message_id", None)
    reply_parameters = ReplyParameters(message_id=reply_to) if reply_to else None
    try:
        await self.send_rich_message(
            chat_id,
            InputRichMessage(html=rich_html),
            reply_markup=markup,
            reply_parameters=reply_parameters,
        )
        return True
    except Exception as err:
        LOGGER.warning(f"send_rich_message gagal ({err.__class__.__name__}): {err}")
    return False


async def _deliver_imdb_result(self, query, res_str, markup, disable_web_preview, thumb, send_as_photo):
    """Kirim hasil IMDb ke chat.

    Prioritas:
    1. send_as_photo + poster -> download lalu edit media foto + caption
    2. caption kepanjangan (MediaCaptionTooLong): EDIT pesan yang ada jadi
       rich message (bukan hapus-lalu-kirim) dengan `<img src="URL">`,
       fallback rich tanpa foto kalau URL gagal
    3. teks kepanjangan tanpa foto (MessageTooLong) -> rich message via edit
    4. selain itu -> edit teks biasa
    """
    if not send_as_photo:
        try:
            await query.message.edit(
                res_str,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=markup,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=disable_web_preview),
            )
            return
        except MessageTooLong:
            if await _send_rich_result(self, query, res_str, markup, None):
                return
            with contextlib.suppress(MessageNotModified, MessageIdInvalid):
                await query.message.edit(
                    res_str[:4090],
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                    link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=disable_web_preview),
                )
            return
    if not thumb:
        return await query.message.edit(
            res_str,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=markup,
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=disable_web_preview),
        )
    caption_too_long = False
    try:
        await self.edit_message_media(
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            media=InputMediaPhoto(thumb, caption=res_str, parse_mode=enums.ParseMode.HTML),
            reply_markup=markup,
        )
        return
    except MediaCaptionTooLong:
        caption_too_long = True
    except MessageNotModified:
        return
    except (PhotoInvalidDimensions, WebpageMediaEmpty):
        thumb = thumb.replace(".jpg", "._V1_UX360.jpg")
        try:
            await self.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(thumb, caption=res_str, parse_mode=enums.ParseMode.HTML),
                reply_markup=markup,
            )
            return
        except Exception as retry_err:
            LOGGER.warning(f"Edit media retry gagal ({thumb}): {retry_err.__class__.__name__}: {retry_err}")
    except Exception as err:
        LOGGER.warning(f"Edit media gagal ({thumb}): {err.__class__.__name__}: {err}")
    if caption_too_long and await _send_rich_result(self, query, res_str, markup, thumb):
        return
    with contextlib.suppress(MessageNotModified, MessageIdInvalid):
        await query.message.edit(
            res_str,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=markup,
            link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=disable_web_preview),
        )


# IMDB Choose Language
@app.on_cmd("imdb")
async def imdb_choose(_, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply(
            f"ℹ️ Please add query after CMD!\nEx: <code>/{ctx.command[0]} Jurassic World</code>",
            del_in=7,
        )
    if ctx.sender_chat:
        return await ctx.reply(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    kuery = ctx.text.split(None, 1)[1]
    is_imdb, lang = await is_imdbset(ctx.from_user.id)
    if is_imdb:
        # "eng" -> "en", selain itu "id" — satu fungsi _imdb_search untuk dua bahasa
        return await _imdb_search(kuery, ctx, "en" if lang == "eng" else "id")
    ranval = get_random_string(4)
    LIST_CARI.add(ranval, kuery, timeout=15)
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🇺🇸 English", callback_data=f"imdbcari#eng#{ranval}#{ctx.from_user.id}"
                ),
                InlineKeyboardButton(
                    "🇮🇩 Indonesia", callback_data=f"imdbcari#ind#{ranval}#{ctx.from_user.id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🚩 Set Default Language", callback_data=f"imdbset#{ctx.from_user.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Close",
                    callback_data=f"close#{ctx.from_user.id}",
                    icon_custom_emoji_id=IMDB_CUSTOM_EMOJI["close"],
                    style=enums.ButtonStyle.DANGER,
                )
            ],
        ]
    )
    await ctx.reply(
        f"Hi {ctx.from_user.mention}, Please select the language you want to use on IMDB Search. If you want use default lang for every user, click third button. So no need click select lang if use CMD.\n\nTimeout: 10s",
        reply_markup=buttons,
    )


@app.on_cmd("imdbtemplate")
async def imdb_template(_, ctx: Message):
    if ctx.sender_chat:
        return await ctx.reply(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    if len(ctx.command) == 1:
        template = await get_imdb_template(ctx.from_user.id)
        placeholders = (
            "{title}, {title_with_year}, {title_link}, {aka}, {type}, {year}, "
            "{duration}, {duration_raw}, {category}, {rating_value}, {rating_count}, "
            "{rating_text}, {release}, {release_url}, {release_link}, {genres}, "
            "{genres_list}, {countries}, {countries_list}, {languages}, "
            "{languages_list}, {directors}, {writers}, {cast}, {plot}, {keywords}, "
            "{keywords_list}, {awards}, {availability}, {ott}, {imdb_by}, "
            "{metacritic_score}, {metacritic_reviews}, {budget}, {opening}, "
            "{domestic}, {worldwide}, {parents_guide}, "
            "{imdb_url}, {trailer_url}, {poster_url}, {imdb_code}, {locale}"
        )
        if template:
            return await ctx.reply(
                "✅ Current IMDb template:\n"
                f"<blockquote><code>{template}</code></blockquote>\n"
                "Use <code>/imdbtemplate reset</code> to remove it.\n\n"
                f"Available placeholders:\n<code>{placeholders}</code>"
            )
        return await ctx.reply(
            "Set a custom IMDb template:\n"
            "<code>/imdbtemplate Title: {title}\\nType: {movie_type}</code>\n\n"
            f"Available placeholders:\n<code>{placeholders}</code>\n\n"
            "Remove template with <code>/imdbtemplate remove</code>.\n"
            "Format tombol: <code>[Label](https://contoh.com)</code>.\n"
            "Gunakan <code>/imdbtemplate show</code> untuk melihat template."
        )
    template_arg = ctx.text.split(None, 1)[1].strip()
    lowered = template_arg.lower()
    if lowered in {"reset", "remove", "delete", "default"}:
        await remove_imdb_template(ctx.from_user.id)
        return await ctx.reply("✅ IMDb template removed.")
    if lowered == "show":
        current = await get_imdb_template(ctx.from_user.id)
        if not current:
            return await ctx.reply("⚠️ IMDb template belum diatur.")
        return await ctx.reply(
            f"✅ Current IMDb template:\n<blockquote><code>{current}</code></blockquote>"
        )
    if lowered.startswith("set"):
        template_value = template_arg[3:].strip()
        if not template_value and ctx.reply_to_message:
            template_value = ctx.reply_to_message.text or ctx.reply_to_message.caption
        if not template_value:
            return await ctx.reply(
                "⚠️ Please provide a template after <code>/imdbtemplate set</code> "
                "or reply to a message containing the template."
            )
        await set_imdb_template(ctx.from_user.id, template_value)
        return await ctx.reply("✅ IMDb template updated.")
    await set_imdb_template(ctx.from_user.id, template_arg)
    await ctx.reply("✅ IMDb template updated.")


@app.on_cmd("imdbby")
async def imdb_by_cmd(_, ctx: Message):
    if ctx.sender_chat:
        return await ctx.reply(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    if len(ctx.command) == 1:
        current = await get_imdb_by(ctx.from_user.id)
        return await ctx.reply(
            "Set IMDb by text:\n"
            "<code>/imdbby YourTextHere</code>\n"
            "Remove with <code>/imdbby remove</code>.\n\n"
            f"Current: <code>{current or f'@{app.me.username}'}</code>"
        )
    value = ctx.text.split(None, 1)[1].strip()
    if value.lower() in {"remove", "reset", "delete"}:
        await remove_imdb_by(ctx.from_user.id)
        return await ctx.reply("✅ IMDb by removed.")
    await set_imdb_by(ctx.from_user.id, value)
    await ctx.reply("✅ IMDb by updated.")


@app.on_cmd("imdbset")
async def imdb_settings_cmd(_, ctx: Message):
    if ctx.sender_chat:
        return await ctx.reply(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    caption = _imdb_settings_caption(ctx.from_user.first_name)
    buttons = _imdb_settings_keyboard(ctx.from_user.id)
    await ctx.reply(caption, reply_markup=buttons)


@app.on_cb("imdbset#")
async def imdblangset(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    buttons = _imdb_settings_keyboard(query.from_user.id)
    caption = _imdb_settings_caption(query.from_user.first_name)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(caption, reply_markup=buttons)


@app.on_cb("imdbsetlang#")
async def imdb_lang_menu(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data=f"setimdb#eng#{query.from_user.id}"),
                InlineKeyboardButton("🇮🇩 Indonesia", callback_data=f"setimdb#ind#{query.from_user.id}"),
            ]
        ]
    )
    is_imdb, _ = await is_imdbset(query.from_user.id)
    if is_imdb:
        buttons.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    "🗑 Remove UserSetting", callback_data=f"setimdb#rm#{query.from_user.id}"
                )
            ]
        )
    buttons.inline_keyboard.append(
        [InlineKeyboardButton("↩️ Back", callback_data=f"imdbset#{query.from_user.id}")]
    )
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(
            "<i>Please select available language below..</i>", reply_markup=buttons
        )


@app.on_cb("imdblayout#")
async def imdb_layout_toggle(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    current = await get_imdb_layout(query.from_user.id)
    await set_imdb_layout(query.from_user.id, not current)
    with contextlib.suppress(QueryIdInvalid):
        await query.answer("✅ Layout diperbarui.")
    caption = _imdb_settings_caption(query.from_user.first_name)
    buttons = _imdb_settings_keyboard(query.from_user.id)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(caption, reply_markup=buttons)


@app.on_cb("imdblayoutmenu#")
async def imdb_layout_menu(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    hidden = await _get_hidden_layout_fields(query.from_user.id)
    buttons = _layout_keyboard(hidden, query.from_user.id)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(_imdb_layout_caption(), reply_markup=buttons)


@app.on_cb("imdblayouttoggle#")
async def imdb_layout_toggle_field(_, query: CallbackQuery):
    _, field_key, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    with contextlib.suppress(QueryIdInvalid):
        await query.answer("✅ Layout diperbarui.")
    hidden = await _toggle_layout_field(query.from_user.id, field_key)
    buttons = _layout_keyboard(hidden, query.from_user.id)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(_imdb_layout_caption(), reply_markup=buttons)


@app.on_cb("imdblayoutreset#")
async def imdb_layout_reset(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    with contextlib.suppress(QueryIdInvalid):
        await query.answer("✅ Layout direset.")
    await reset_imdb_layout_fields(query.from_user.id)
    buttons = _layout_keyboard(set(), query.from_user.id)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(_imdb_layout_caption(), reply_markup=buttons)


@app.on_cb("imdbtemplatemenu#")
async def imdb_template_menu(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    template = await get_imdb_template(query.from_user.id)
    status = "Sudah diatur ✅" if template else "Belum diatur ❌"
    text = (
        f"<b>Custom Layout IMDb</b>\nStatus: {status}\n\n"
        "<b>Perintah:</b>\n"
        "• <code>/imdbtemplate set</code> + template di pesan yang sama.\n"
        "• Atau balas pesan berisi template dengan <code>/imdbtemplate set</code>.\n"
        "• <code>/imdbtemplate remove</code> untuk menghapus.\n"
        "• <code>/imdbtemplate show</code> untuk melihat template.\n"
        "• Tombol dapat dibuat dengan format <code>[Label](https://contoh.com)</code>.\n\n"
        "<b>Placeholder:</b>\n"
        "• <code>{title}</code> - Judul utama\n"
        "• <code>{title_with_year}</code> - Judul + tahun\n"
        "• <code>{title_link}</code> - Judul + tahun versi tautan\n"
        "• <code>{aka}</code> - Judul alternatif (AKA)\n"
        "• <code>{type}</code> - Jenis konten (Movie, Series, dll)\n"
        "• <code>{year}</code> - Rentang/tahun perilisan\n"
        "• <code>{duration}</code> - Durasi (diterjemahkan untuk ID)\n"
        "• <code>{duration_raw}</code> - Durasi asli dari IMDb\n"
        "• <code>{category}</code> - Rating konten (PG-13, dll)\n"
        "• <code>{rating_value}</code> - Nilai rating IMDb\n"
        "• <code>{rating_count}</code> - Total penilai\n"
        "• <code>{rating_text}</code> - Ringkasan rating sesuai bahasa\n"
        "• <code>{release}</code> - Tanggal rilis\n"
        "• <code>{release_url}</code> - Tautan tanggal rilis\n"
        "• <code>{release_link}</code> - Tanggal rilis versi tautan\n"
        "• <code>{genres}</code> - Genre dalam bentuk hashtag\n"
        "• <code>{genres_list}</code> - Genre dipisah koma\n"
        "• <code>{countries}</code> - Daftar negara + hashtag\n"
        "• <code>{countries_list}</code> - Daftar negara biasa\n"
        "• <code>{languages}</code> - Daftar bahasa + hashtag\n"
        "• <code>{languages_list}</code> - Daftar bahasa biasa\n"
        "• <code>{directors}</code> - Daftar sutradara\n"
        "• <code>{writers}</code> - Daftar penulis\n"
        "• <code>{cast}</code> - Daftar pemeran\n"
        "• <code>{plot}</code> - Plot / summary\n"
        "• <code>{keywords}</code> - Daftar kata kunci versi hashtag\n"
        "• <code>{keywords_list}</code> - Daftar kata kunci dipisah koma\n"
        "• <code>{awards}</code> - Informasi penghargaan\n"
        "• <code>{availability}</code> - Info layanan streaming\n"
        "• <code>{ott}</code> - Data mentah dari pencarian OTT\n"
        "• <code>{imdb_by}</code> - Tagline @username bot\n"
        "• <code>{imdb_url}</code> - URL halaman IMDb\n"
        "• <code>{trailer_url}</code> - URL trailer\n"
        "• <code>{poster_url}</code> - URL poster\n"
        "• <code>{imdb_code}</code> - ID IMDb (misal tt1234567)\n"
        "• <code>{locale}</code> - Kode bahasa (id/en)\n"
        "• <code>{nama_placeholder_html}</code> - versi aman HTML (otomatis tersedia)\n"
        "  Contoh: <code>{plot_html}</code>\n\n"
        "Catatan: ketika template aktif, pengaturan layout bawaan diabaikan "
        "(kecuali Link Preview)."
    )
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("↩️ Back", callback_data=f"imdbset#{query.from_user.id}"),
                InlineKeyboardButton(
                    "Close",
                    callback_data=f"close#{query.from_user.id}",
                    icon_custom_emoji_id=IMDB_CUSTOM_EMOJI["close"],
                    style=enums.ButtonStyle.DANGER,
                ),
            ]
        ]
    )
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(text, reply_markup=buttons)


@app.on_cb("imdby#")
async def imdb_by_menu(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    current = await get_imdb_by(query.from_user.id) or f"@{app.me.username}"
    text = (
        "<b>Edit IMDb by</b>\n"
        "Gunakan perintah:\n"
        "<code>/imdbby Teks_kamu</code>\n"
        "Hapus dengan <code>/imdbby remove</code>.\n\n"
        f"Current: <code>{current}</code>"
    )
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("↩️ Back", callback_data=f"imdbset#{query.from_user.id}")]
        ]
    )
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(text, reply_markup=buttons)


@app.on_cb("setimdb")
async def imdbsetlang(_, query: CallbackQuery):
    _, lang, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    _, langset = await is_imdbset(query.from_user.id)
    if langset == lang:
        return await query.answer(f"⚠️ Your Setting Already in ({langset})!", True)
    if lang == "eng":
        await add_imdbset(query.from_user.id, lang)
        msg_text = "Language interface for IMDB has been changed to English."
    elif lang == "ind":
        await add_imdbset(query.from_user.id, lang)
        msg_text = "Bahasa tampilan IMDB sudah diubah ke Indonesia."
    else:
        await remove_imdbset(query.from_user.id)
        msg_text = "UserSetting for IMDB has been deleted from database."
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "↩️ Back", callback_data=f"imdbset#{query.from_user.id}"
                )
            ]
        ]
    )
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(msg_text, reply_markup=buttons)


async def _imdb_search(kueri, message, locale: str = "id", edit_msg=None, with_mention: bool = False, user_id: int | None = None, mention: str | None = None):
    """Cari judul di database suggestion IMDb, tampilkan list hasil + tombol.

    ``locale`` menentukan bahasa teks ("id" / "en"). ``edit_msg`` diisi untuk
    meng-edit pesan yang sudah ada (dipakai callback imdbcari), kalau None
    pesan baru di-reply. ``with_mention`` menambah "~ @user" di header hasil.
    ``user_id``/``mention`` di-override saat pesan bukan dari user langsung
    (callback: query.message.from_user = bot). Satu fungsi untuk semua jalur
    pencarian (command & callback).
    """
    is_id = locale == "id"
    S = _IMDB_SEARCH_STRINGS.get(locale, _IMDB_SEARCH_STRINGS["id"])
    uid = user_id if user_id is not None else (message.from_user.id if message.from_user else 0)
    mention_text = mention if mention is not None else (message.from_user.mention if message.from_user else "")
    BTN = []
    k = edit_msg or await message.reply(S["searching"].format(q=kueri))
    msg = ""
    with contextlib.redirect_stdout(sys.stderr):
        try:
            r = await fetch.get(
                f"https://v3.sg.media-imdb.com/suggestion/titles/x/{quote_plus(kueri)}.json"
            )
            r.raise_for_status()
            res = r.json().get("d")
            if not res:
                return await k.edit(S["notfound"].format(q=kueri))
            if with_mention:
                msg += S["found"].format(n=len(res), q=kueri) + f" ~ {mention_text}\n\n"
            else:
                msg += S["found"].format(n=len(res), q=kueri)
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
                        callback_data=f"imdbres_{'id' if is_id else 'en'}#{uid}#{movieID}",
                    )
                )
            # Tombol nomor 4-per-baris + Language + Close (baris sendiri)
            rows = [BTN[i : i + 4] for i in range(0, len(BTN), 4)]
            rows.append(
                [
                    InlineKeyboardButton(
                        text="🚩 Language",
                        callback_data=f"imdbsetlang#{uid}",
                    )
                ]
            )
            rows.append(
                [
                    InlineKeyboardButton(
                        text="Close",
                        callback_data=f"close#{uid}",
                        icon_custom_emoji_id=IMDB_CUSTOM_EMOJI["close"],
                        style=enums.ButtonStyle.DANGER,
                    )
                ]
            )
            await k.edit(msg, reply_markup=InlineKeyboardMarkup(rows))
        except httpx.HTTPError as exc:
            await k.edit(S["http_err"].format(exc=exc))
        except (MessageIdInvalid, MessageNotModified):
            pass
        except Exception as err:
            await k.edit(S["err"].format(err=err))


_IMDB_SEARCH_STRINGS = {
    "id": {
        "searching": "🔎 Menelusuri <code>{q}</code> di database IMDb ...",
        "notfound": "⛔️ Tidak ditemukan hasil untuk kueri: <code>{q}</code>",
        "found": "🎬 Ditemukan ({n}) hasil untuk kueri: <code>{q}</code>\n\n",
        "http_err": "HTTP Exception for IMDB Search - <code>{exc}</code>",
        "err": (
            "Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena "
            "rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>"
        ),
    },
    "en": {
        "searching": "🔎 Searching <code>{q}</code> in IMDb Database...",
        "notfound": "⛔️ Result not found for keywords: <code>{q}</code>",
        "found": "🎬 Found ({n}) result for keywords: <code>{q}</code>\n\n",
        "http_err": "HTTP Exception for IMDB Search - <code>{exc}</code>",
        "err": (
            "Failed when requesting movies title. Maybe got rate limit or down."
            "\n\n<b>ERROR:</b> <code>{err}</code>"
        ),
    },
}


@app.on_cb("imdbcari")
async def imdbcari(_, query: CallbackQuery):
    _, lang, msg, uid = query.data.split("#")
    locale = "id" if lang == "ind" else "en"
    denied = "⚠️ Akses Ditolak!" if locale == "id" else "⚠️ Access Denied!"
    expired = "⚠️ Callback Query Sudah Expired!" if locale == "id" else "⚠️ Callback Query Expired!"
    if query.from_user.id != int(uid):
        return await query.answer(denied, True)
    try:
        kueri = LIST_CARI.get(msg)
        del LIST_CARI[msg]
    except KeyError:
        return await query.message.edit(expired)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit(
            "<i>🔎 Sedang mencari di Database IMDB..</i>"
            if locale == "id"
            else "<i>🔎 Looking in the IMDB Database..</i>"
        )
    # Satu jalur pencarian (id/en) — imdbcari hanya memilih bahasa.
    await _imdb_search(
        kueri,
        query.message,
        locale=locale,
        edit_msg=query.message,
        with_mention=True,
        user_id=int(uid),
        mention=query.from_user.mention,
    )


# =====================================================================
# Labels per locale — satu-satunya perbedaan antara hasil ID dan EN.
# =====================================================================
IMDB_CUSTOM_EMOJI = {
    "processing": "5319190934510904031",  # ⏳
    "cast": "5879770735999717115",  # 🙎
    "plot": "5956561916573782596",  # 📜
    "keywords": "6008118472066732010",  # 🔥
    "title": "6005986106703613755",  # 📹
    "aka": "6039454987250044861",  # 📢
    "duration": "5900104897885376843",  # 🕓
    "category": "5920137394153067262",  # 🔞
    "awards": "6035162669948867129",  # 🏆
    "rating": "6035162669948867129",  # 🏆
    "released": "5967412305338568701",  # 📆
    "genre": "6032625495328165724",  # 🎭
    "country": "5776424837786374634",  # 🆔
    "language": "5890997763331591703",  # 🔊
    "rating_star": "6028338546736107668",  # ⭐
    "close": "5985346521103604145",  # ❌ (tombol Close)
    "imdb_by": "5886440807325504167",  # ©️
}


def _ce(key: str, glyph: str) -> str:
    return f'<emoji id="{IMDB_CUSTOM_EMOJI[key]}">{glyph}</emoji>'


_IMDB_LABELS = {
    "id": {
        "processing": f"<i>{_ce('processing', '⏳')} Permintaan kamu sedang diproses.. </i>",
        "search_jw_locale": "ID",
        "date_locale": "id",
        "translate": True,
        "title": f"{_ce('title', '📹')} Judul:",
        "aka": f"{_ce('aka', '📢')} AKA:",
        "duration": f"{_ce('duration', '🕓')} Durasi:",
        "category": f"{_ce('category', '🔞')} Kategori:",
        "rating": f"{_ce('rating', '🏆')} Peringkat:",
        "rating_from": "dari {count} pengguna",
        "release": f"{_ce('released', '📆')} Rilis:",
        "genre": f"{_ce('genre', '🎭')} Genre:",
        "country": f"{_ce('country', '🆔')} Negara:",
        "language": f"{_ce('language', '🔊')} Bahasa:",
        "cast_header": f"{_ce('cast', '🙎')} Info Cast:",
        "director": "Sutradara:",
        "writer": "Penulis:",
        "actor": "Pemeran:",
        "plot": f"{_ce('plot', '📜')} Plot:",
        "keywords": f"{_ce('keywords', '🔥')} Kata Kunci:",
        "awards": f"{_ce('awards', '🏆')} Penghargaan:",
        "available": f"{_ce('available', '📽')} Tersedia di:",
        "imdb_by": f"{_ce('imdb_by', '©️')} IMDb by",
        "http_err": "HTTP Exception for IMDB Search - <code>{exc}</code>",
        "parse_err": (
            "Maaf, gagal mendapatkan info data dari IMDB.\n"
            "<blockquote><code>{err}</code></blockquote>\n"
            "<blockquote expandable><code>{exc}</code></blockquote>"
        ),
    },
    "en": {
        "processing": f"<i>{_ce('processing', '⏳')} Getting IMDb source..</i>",
        "search_jw_locale": "US",
        "date_locale": "en",
        "translate": False,
        "title": f"{_ce('title', '📹')} Title:",
        "aka": f"{_ce('aka', '📢')} AKA:",
        "duration": f"{_ce('duration', '🕓')} Duration:",
        "category": f"{_ce('category', '🔞')} Category:",
        "rating": f"{_ce('rating', '🏆')} Rating:",
        "rating_from": "from {count} users",
        "release": f"{_ce('released', '📆')} Released:",
        "genre": f"{_ce('genre', '🎭')} Genre:",
        "country": f"{_ce('country', '🆔')} Country:",
        "language": f"{_ce('language', '🔊')} Language:",
        "cast_header": f"{_ce('cast', '🙎')} Cast Info:",
        "director": "Director:",
        "writer": "Writer:",
        "actor": "Stars:",
        "plot": f"{_ce('plot', '📜')} Summary:",
        "keywords": f"{_ce('keywords', '🔥')} Keywords:",
        "awards": f"{_ce('awards', '🏆')} Awards:",
        "available": f"{_ce('available', '📽')} Available On:",
        "imdb_by": f"{_ce('imdb_by', '©️')} IMDb by",
        "http_err": "HTTP Exception for IMDB Search - <code>{exc}</code>",
        "parse_err": (
            "Sorry, failed getting data from IMDB.\n"
            "<blockquote><code>{err}</code></blockquote>\n"
            "<blockquote expandable><code>{exc}</code></blockquote>"
        ),
    },
}

_RATING_STAR = _ce("rating_star", "⭐")


async def _build_imdb_result(
    r_json, movie, imdb_url, locale, template, hidden_fields, imdb_by, ott, uid: int = 0
):
    """Rangkai hasil detail IMDb menjadi satu pesan.

    Mengembalikan ``(res_str, markup, disable_web_preview, send_as_photo)``.
    Setiap baris disimpan di dict ``lines`` supaya penghapusan field
    tersembunyi (layout) tepat sasaran — tidak perlu string replace yang
    rapuh seperti sebelumnya.
    """
    L = _IMDB_LABELS[locale]
    lines: dict = {}
    template_markup: InlineKeyboardMarkup | None = None
    typee = r_json.get("@type", "")
    tahun = str(r_json.get("releaseYear") or "N/A")

    # ---- data vars (dipakai untuk payload template) ----
    duration_raw = "-"
    duration_text = "-"
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
    awards_id_text = "-"
    # Tanggal rilis mentah dari GraphQL (dipakai payload template {release}).
    # GraphQL IMDb tidak menyediakan URL spesifik per tanggal rilis, jadi
    # rilis_url sengaja dikosongkan -> {release_url}/{release_link} = "-".
    rilis = r_json.get("datePublished") or "-"
    rilis_url = ""
    summary = ""
    genre_list = []
    country_list = []
    language_list = []
    director_names = []
    writer_names = []
    actor_names = []
    cast_lines = []

    # ---- judul + AKA ----
    lines["title"] = (
        f"<b>{L['title']}</b> <a href=\"{imdb_url}\">{r_json.get('name')} [{tahun}]</a> "
        f"(<code>{typee}</code>)\n"
    )
    if aka := r_json.get("alternateName"):
        lines["aka"] = f"<b>{L['aka']}</b> <code>{aka}</code>\n\n"
    else:
        lines["aka"] = "\n"

    # ---- detail singkat ----
    if durasi := r_json.get("duration"):
        duration_raw = durasi
        if L["translate"]:
            duration_text = (await gtranslate(durasi, "auto", "id")).text
        else:
            duration_text = durasi
        lines["duration"] = f"<b>{L['duration']}</b> <code>{duration_text}</code>\n"
    if kategori := r_json.get("contentRating"):
        category_text = kategori or "-"
        lines["category"] = f"<b>{L['category']}</b> <code>{kategori}</code> \n"
    rating_value = "-"
    rating_count = "-"
    if rating := r_json.get("aggregateRating"):
        rating_value = rating.get("ratingValue", "-")
        rating_count = rating.get("ratingCount", "-")
        # Star custom emoji DI LUAR <code> — emoji di dalam code tidak render.
        lines["rating"] = (
            f"<b>{L['rating']}</b> <code>{rating_value}</code> "
            f"{_RATING_STAR} {L['rating_from'].format(count=rating_count)}\n"
        )
    if rilis != "-":
        release_date_text = format_imdb_date(rilis, L["date_locale"]) or rilis
        lines["release_date"] = f"<b>{L['release']}</b> <code>{release_date_text}</code>\n"
    if genre := r_json.get("genre"):
        genre_list = genre if isinstance(genre, list) else [genre]
        genre_text = "".join(
            f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, "
            if i in GENRES_EMOJI
            else f"#{i.replace('-', '_').replace(' ', '_')}, "
            for i in genre_list
        )
        lines["genre"] = f"<b>{L['genre']}</b> {genre_text[:-2]}\n"
    if genre_text == "-":
        genre_text = "-"
    else:
        genre_text = genre_text[:-2]
    if countries := r_json.get("countryOfOrigin"):
        country_items = countries if isinstance(countries, list) else [countries]
        country_list = [str(country) for country in country_items if country]
        country_text = "".join(
            f"{demoji(str(country))} #{str(country).replace(' ', '_').replace('-', '_')}, "
            for country in country_items
            if country
        )
        lines["country"] = f"<b>{L['country']}</b> {country_text[:-2]}\n"
    if country_text == "-":
        country_text = "-"
    else:
        country_text = country_text[:-2]
    if languages := r_json.get("inLanguage"):
        language_items = languages if isinstance(languages, list) else [languages]
        language_list = [str(lang) for lang in language_items if lang]
        language_text = "".join(
            f"#{str(lang).replace(' ', '_').replace('-', '_')}, "
            for lang in language_items
            if lang
        )
        lines["language"] = f"<b>{L['language']}</b> {language_text[:-2]}\n"
    if language_text == "-":
        language_text = "-"
    else:
        language_text = language_text[:-2]

    # ---- cast ----
    lines["cast_header"] = f"\n<b>{L['cast_header']}</b>\n"
    if directors := r_json.get("director"):
        director_names = [item["name"] for item in directors]
        director = "".join(
            f"<a href='{i['url']}'>{i['name']}</a>, " for i in directors
        )
        director_text = director[:-2] if director else "-"
        cast_lines.append(f"{L['director'].rstrip(':')}: {director_text}")
        lines["director"] = f"<b>{L['director']}</b> {director[:-2]}\n"
    if creators := r_json.get("creator"):
        writer_names = [
            i["name"] for i in creators if i.get("@type") == "Person"
        ]
        creator = "".join(
            f"<a href='{i['url']}'>{i['name']}</a>, "
            for i in creators
            if i.get("@type") == "Person"
        )
        writer_text = creator[:-2] if creator else "-"
        cast_lines.append(f"{L['writer'].rstrip(':')}: {writer_text}")
        lines["writer"] = f"<b>{L['writer']}</b> {creator[:-2]}\n"
    if actors := r_json.get("actor"):
        actor_names = [i["name"] for i in actors]
        actor = "".join(
            f"<a href='{i['url']}'>{i['name']}</a>, " for i in actors
        )
        cast_text = actor[:-2] if actor else "-"
        cast_lines.append(f"{L['actor'].rstrip(':')}: {cast_text}")
        lines["actor"] = f"<b>{L['actor']}</b> {actor[:-2]}\n\n"
    cast_info = "\n".join(cast_lines) if cast_lines else "-"

    # ---- plot / keywords / awards ----
    if deskripsi := r_json.get("description"):
        if L["translate"]:
            summary = (await gtranslate(deskripsi, "auto", "id")).text
        else:
            summary = deskripsi
        storyline_text = summary or "-"
        # Label + blockquote SATU baris — rich message render label rapat
        # dengan <details> (tidak ada enter di antara).
        lines["plot"] = (
            f"<b>{L['plot']}</b><blockquote expandable><code>{summary}</code></blockquote>\n\n"
        )
    keywords_list = []
    if keywd := r_json.get("keywords"):
        keywords_list = [kw.strip() for kw in keywd.split(",")]
        keyword_text = "".join(
            f"#{i.replace(' ', '_').replace('-', '_')}, "
            for i in keywords_list
        )
        lines["keywords"] = (
            f"<b>{L['keywords']}</b><blockquote expandable>{keyword_text[:-2]}</blockquote>\n\n"
        )
    if keyword_text != "-":
        keyword_text = keyword_text[:-2]
    if r_json.get("awards_counts"):
        awards_text = r_json.get("awards_en") or "-"
        awards_id_text = format_imdb_awards(r_json.get("awards_counts"), "id") or "-"
        display_awards = awards_id_text if locale == "id" else awards_text
        lines["awards"] = (
            f"<b>{L['awards']}</b><blockquote expandable><code>{display_awards}</code></blockquote>\n\n"
        )
    else:
        lines["awards_spacer"] = "\n"
    if ott != "":
        lines["ott"] = f"<b>{L['available']}</b>\n{ott}\n"
    ott_value = ott or "-"
    lines["imdb_by"] = f"<b>{L['imdb_by']}</b> {imdb_by}"

    res_str = "".join(lines.values())

    # ---- template custom user ----
    if template:
        imdb_code = f"tt{movie}"
        title = r_json.get("name") or "-"
        year_text = tahun
        title_with_year = f"{title} [{year_text}]"
        title_link = f"<a href=\"{imdb_url}\">{title_with_year}</a>"
        aka_text = r_json.get("alternateName") or "-"
        rating_value = "-"
        rating_count = "-"
        rating_text = "-"
        if rating := r_json.get("aggregateRating"):
            rating_value = rating.get("ratingValue", "-")
            rating_count = rating.get("ratingCount", "-")
            rating_text = (
                f"{rating_value}{_RATING_STAR} "
                f"{L['rating_from'].format(count=rating_count)}"
            )
        release_url = f"https://www.imdb.com{rilis_url}" if rilis_url else "-"
        release_link = f"<a href=\"{release_url}\">{rilis}</a>" if rilis_url else "-"
        poster_url = r_json.get("image") or "-"
        trailer_url = (r_json.get("trailer") or {}).get("url") or "-"
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
            "awards_en": r_json.get("awards_en") or "-",
            "awards_id": awards_id_text,
            "awards_counts": r_json.get("awards_counts") or {},
            "metacritic_score": str((r_json.get("metacritic") or {}).get("score") or "-"),
            "metacritic_reviews": str((r_json.get("metacritic") or {}).get("reviewCount") or "-"),
            "budget": format_imdb_money(r_json.get("budget")),
            "opening": format_imdb_money(r_json.get("opening")),
            "domestic": format_imdb_money(r_json.get("domestic")),
            "worldwide": format_imdb_money(r_json.get("worldwide")),
            "parents_guide": ", ".join(
                item.get("category", "") for item in r_json.get("parents_guide") or [] if item.get("category")
            ) or "-",
            "availability": ott_value,
            "ott": ott_value,
            "imdb_by": imdb_by,
            "imdb_url": imdb_url,
            "trailer_url": trailer_url,
            "poster_url": poster_url,
            "imdb_code": imdb_code,
            "locale": locale,
            "link": imdb_url,
            "movie_type": typee or "-",
            "release_date": release_date_text,
            "genre": genre_text,
            "country": country_text,
            "language": language_text,
            "director": director_text,
            "writer": writer_text,
            "cast_info": cast_info,
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
        # ---- layout: buang field yang disembunyikan user ----
        _HIDDEN_FIELD_LINES = {
            "title": ["title"],
            "duration": ["duration"],
            "category": ["category"],
            "rating": ["rating"],
            "release_date": ["release_date"],
            "genre": ["genre"],
            "country": ["country"],
            "language": ["language"],
            "cast": ["cast_header", "director", "writer", "actor"],
            "storyline": ["plot"],
            "keyword": ["keywords"],
            "awards": ["awards"],
            "ott": ["ott"],
            "imdb_by": ["imdb_by"],
        }
        for field, line_keys in _HIDDEN_FIELD_LINES.items():
            if field in hidden_fields:
                for line_key in line_keys:
                    res_str = res_str.replace(lines.get(line_key, ""), "")

    # ---- tombol ----
    # Tombol Close custom emoji: label tanpa emoji teks (icon custom emoji
    # sudah menampilkan ❌ — label ber-emoji teks jadi dobel).
    close_btn = InlineKeyboardButton(
        "Close",
        callback_data=f"close#{uid}",
        icon_custom_emoji_id=IMDB_CUSTOM_EMOJI["close"],
        style=enums.ButtonStyle.DANGER,
    )
    if template:
        if template_markup:
            template_markup.inline_keyboard.append([close_btn])
            markup = template_markup
        else:
            markup = InlineKeyboardMarkup([[close_btn]])
    else:
        if trailer := r_json.get("trailer"):
            trailer_url = trailer["url"]
            buttons = []
            if "open_imdb" not in hidden_fields:
                buttons.append(InlineKeyboardButton("🎬 Open IMDB", url=imdb_url))
            if "trailer" not in hidden_fields:
                buttons.append(InlineKeyboardButton("▶️ Trailer", url=trailer_url))
            rows = [buttons] if buttons else []
            # Close SELALU di baris sendiri di bawah (tidak berjejer)
            rows.append([close_btn])
            markup = InlineKeyboardMarkup(rows)
        else:
            if "open_imdb" in hidden_fields:
                markup = InlineKeyboardMarkup([[close_btn]])
            else:
                markup = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)],
                        [close_btn],
                    ]
                )
    disable_web_preview = "web_preview" in hidden_fields
    send_as_photo = "send_as_photo" not in hidden_fields
    return res_str, markup, disable_web_preview, send_as_photo


async def _process_imdb_callback(self: Client, query: CallbackQuery, movie: str, locale: str):
    """Alur detail IMDb (dipakai callback id & en — bedanya hanya label)."""
    L = _IMDB_LABELS[locale]
    with contextlib.redirect_stdout(sys.stderr):
        try:
            await query.message.edit(L["processing"])
            imdb_url = f"https://m.imdb.com/title/tt{movie}/"
            r_json = await get_imdb_details_graphql(f"tt{movie}")
            if not r_json:
                raise ValueError("IMDb GraphQL returned empty payload")
            ott = await search_jw(
                r_json.get("alternateName") or r_json.get("name"), L["search_jw_locale"]
            )
            template = await get_imdb_template(query.from_user.id)
            hidden_fields = await _get_hidden_layout_fields(query.from_user.id)
            imdb_by = await get_imdb_by(query.from_user.id) or f"@{self.me.username}"
            res_str, markup, disable_web_preview, send_as_photo = await _build_imdb_result(
                r_json,
                movie,
                imdb_url,
                locale,
                template,
                hidden_fields,
                imdb_by,
                ott,
                uid=query.from_user.id,
            )
            await _deliver_imdb_result(
                self,
                query,
                res_str,
                markup,
                disable_web_preview,
                r_json.get("image"),
                send_as_photo,
            )
        except httpx.HTTPError as exc:
            await query.message.edit(L["http_err"].format(exc=exc))
        except (AttributeError, ValueError) as err:
            LOGGER.exception(f"IMDb {locale} callback failed while parsing IMDb payload")
            exc = traceback.format_exc(limit=5)
            await query.message.edit(
                L["parse_err"].format(err=err, exc=exc),
                parse_mode=enums.ParseMode.HTML,
                link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True),
            )
        except (MessageNotModified, MessageIdInvalid):
            pass


@app.on_cb("imdbres")
async def imdbres_callback(self: Client, query: CallbackQuery):
    # data: imdbres_id#uid#tt1234567 atau imdbres_en#uid#tt1234567
    prefix, userid, movie = query.data.split("#")
    locale = "en" if prefix.endswith("_en") else "id"
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    await _process_imdb_callback(self, query, movie, locale)
