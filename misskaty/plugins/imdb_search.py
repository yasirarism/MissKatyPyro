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
from typing import Optional
from urllib.parse import quote_plus

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
    QueryIdInvalid,
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
from utils import demoji

LOGGER = logging.getLogger("MissKaty")
LIST_CARI = Cache(filename="imdb_cache.db", path="cache", in_memory=False)


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


def render_imdb_template(template: str, payload: dict) -> Optional[str]:
    try:
        normalized = template.replace("\\n", "\n")
        rendered = normalized.format_map(_ImdbTemplateDefaults(payload))
        return re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<a href=\"\2\">\1</a>", rendered
        )
    except Exception as err:
        LOGGER.warning(f"Failed rendering IMDB template: {err}")
        return None


def _with_html_placeholders(payload: dict) -> dict:
    enriched = dict(payload)
    for key, value in payload.items():
        if value is None:
            value = "-"
        if isinstance(value, str):
            enriched[f"{key}_html"] = html.escape(value)
    return enriched


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
            [InlineKeyboardButton("❌ Close", callback_data=f"close#{uid}")],
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
    rows.append([InlineKeyboardButton("❌ Close", callback_data=f"close#{uid}")])
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
    await ctx.reply_msg(
        f"Hi {ctx.from_user.mention}, Please select the language you want to use on IMDB Search. If you want use default lang for every user, click third button. So no need click select lang if use CMD.\n\nTimeout: 10s",
        reply_markup=buttons,
        quote=True,
    )


@app.on_cmd("imdbtemplate")
async def imdb_template(_, ctx: Message):
    if ctx.sender_chat:
        return await ctx.reply_msg(
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
            "{imdb_url}, {trailer_url}, {poster_url}, {imdb_code}, {locale}"
        )
        if template:
            return await ctx.reply_msg(
                "✅ Current IMDb template:\n"
                f"<blockquote><code>{template}</code></blockquote>\n"
                "Use <code>/imdbtemplate reset</code> to remove it.\n\n"
                f"Available placeholders:\n<code>{placeholders}</code>"
            )
        return await ctx.reply_msg(
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
        return await ctx.reply_msg("✅ IMDb template removed.")
    if lowered == "show":
        current = await get_imdb_template(ctx.from_user.id)
        if not current:
            return await ctx.reply_msg("⚠️ IMDb template belum diatur.")
        return await ctx.reply_msg(
            f"✅ Current IMDb template:\n<blockquote><code>{current}</code></blockquote>"
        )
    if lowered.startswith("set"):
        template_value = template_arg[3:].strip()
        if not template_value and ctx.reply_to_message:
            template_value = ctx.reply_to_message.text or ctx.reply_to_message.caption
        if not template_value:
            return await ctx.reply_msg(
                "⚠️ Please provide a template after <code>/imdbtemplate set</code> "
                "or reply to a message containing the template."
            )
        await set_imdb_template(ctx.from_user.id, template_value)
        return await ctx.reply_msg("✅ IMDb template updated.")
    await set_imdb_template(ctx.from_user.id, template_arg)
    await ctx.reply_msg("✅ IMDb template updated.")


@app.on_cmd("imdbby")
async def imdb_by_cmd(_, ctx: Message):
    if ctx.sender_chat:
        return await ctx.reply_msg(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    if len(ctx.command) == 1:
        current = await get_imdb_by(ctx.from_user.id)
        return await ctx.reply_msg(
            "Set IMDb by text:\n"
            "<code>/imdbby YourTextHere</code>\n"
            "Remove with <code>/imdbby remove</code>.\n\n"
            f"Current: <code>{current or f'@{app.me.username}'}</code>"
        )
    value = ctx.text.split(None, 1)[1].strip()
    if value.lower() in {"remove", "reset", "delete"}:
        await remove_imdb_by(ctx.from_user.id)
        return await ctx.reply_msg("✅ IMDb by removed.")
    await set_imdb_by(ctx.from_user.id, value)
    await ctx.reply_msg("✅ IMDb by updated.")


@app.on_cmd("imdbset")
async def imdb_settings_cmd(_, ctx: Message):
    if ctx.sender_chat:
        return await ctx.reply_msg(
            "Cannot identify user, please use in private chat.", del_in=7
        )
    caption = _imdb_settings_caption(ctx.from_user.first_name)
    buttons = _imdb_settings_keyboard(ctx.from_user.id)
    await ctx.reply_msg(caption, reply_markup=buttons)


@app.on_cb("imdbset#")
async def imdblangset(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    buttons = _imdb_settings_keyboard(query.from_user.id)
    caption = _imdb_settings_caption(query.from_user.first_name)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit_msg(caption, reply_markup=buttons)


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
        await query.message.edit_msg(
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
        await query.message.edit_msg(caption, reply_markup=buttons)


@app.on_cb("imdblayoutmenu#")
async def imdb_layout_menu(_, query: CallbackQuery):
    _, uid = query.data.split("#")
    if query.from_user.id != int(uid):
        return await query.answer("⚠️ Access Denied!", True)
    hidden = await _get_hidden_layout_fields(query.from_user.id)
    buttons = _layout_keyboard(hidden, query.from_user.id)
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit_msg(_imdb_layout_caption(), reply_markup=buttons)


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
        await query.message.edit_msg(_imdb_layout_caption(), reply_markup=buttons)


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
        await query.message.edit_msg(_imdb_layout_caption(), reply_markup=buttons)


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
                InlineKeyboardButton("❌ Close", callback_data=f"close#{query.from_user.id}"),
            ]
        ]
    )
    with contextlib.suppress(MessageIdInvalid, MessageNotModified):
        await query.message.edit_msg(text, reply_markup=buttons)


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
        await query.message.edit_msg(text, reply_markup=buttons)


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
        await query.message.edit_msg(msg_text, reply_markup=buttons)


async def imdb_search_id(kueri, message):
    BTN = []
    k = await message.reply_msg(
        f"🔎 Menelusuri <code>{kueri}</code> di database IMDb ...",
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
                return await k.edit_msg(
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
                        callback_data=f"imdbsetlang#{message.from_user.id}",
                    ),
                    InlineKeyboardButton(
                        text="❌ Close",
                        callback_data=f"close#{message.from_user.id}",
                    ),
                )
            )
            buttons.add(*BTN)
            await k.edit_msg(msg, reply_markup=buttons)
        except httpx.HTTPError as exc:
            await k.edit_msg(f"HTTP Exception for IMDB Search - <code>{exc}</code>")
        except (MessageIdInvalid, MessageNotModified):
            pass
        except Exception as err:
            await k.edit_msg(
                f"Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>"
            )


async def imdb_search_en(kueri, message):
    BTN = []
    k = await message.reply_msg(
        f"🔎 Searching <code>{kueri}</code> in IMDb Database...",
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
                return await k.edit_msg(
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
                        callback_data=f"imdbsetlang#{message.from_user.id}",
                    ),
                    InlineKeyboardButton(
                        text="❌ Close",
                        callback_data=f"close#{message.from_user.id}",
                    ),
                )
            )
            buttons.add(*BTN)
            await k.edit_msg(msg, reply_markup=buttons)
        except httpx.HTTPError as exc:
            await k.edit_msg(f"HTTP Exception for IMDB Search - <code>{exc}</code>")
        except (MessageIdInvalid, MessageNotModified):
            pass
        except Exception as err:
            await k.edit_msg(
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
            return await query.message.edit_msg("⚠️ Callback Query Sudah Expired!")
        with contextlib.suppress(MessageIdInvalid, MessageNotModified):
            await query.message.edit_msg("<i>🔎 Sedang mencari di Database IMDB..</i>")
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
                    return await query.message.edit_msg(
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
                            text="🚩 Language", callback_data=f"imdbsetlang#{uid}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Close", callback_data=f"close#{uid}"
                        ),
                    )
                )
                buttons.add(*BTN)
                await query.message.edit_msg(msg, reply_markup=buttons)
            except httpx.HTTPError as exc:
                await query.message.edit_msg(
                    f"HTTP Exception for IMDB Search - <code>{exc}</code>"
                )
            except (MessageIdInvalid, MessageNotModified):
                pass
            except Exception as err:
                await query.message.edit_msg(
                    f"Ooppss, gagal mendapatkan daftar judul di IMDb. Mungkin terkena rate limit atau down.\n\n<b>ERROR:</b> <code>{err}</code>"
                )
    else:
        if query.from_user.id != int(uid):
            return await query.answer("⚠️ Access Denied!", True)
        try:
            kueri = LIST_CARI.get(msg)
            del LIST_CARI[msg]
        except KeyError:
            return await query.message.edit_msg("⚠️ Callback Query Expired!")
        await query.message.edit_msg("<i>🔎 Looking in the IMDB Database..</i>")
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
                    return await query.message.edit_msg(
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
                            text="🚩 Language", callback_data=f"imdbsetlang#{uid}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Close", callback_data=f"close#{uid}"
                        ),
                    )
                )
                buttons.add(*BTN)
                await query.message.edit_msg(msg, reply_markup=buttons)
            except httpx.HTTPError as exc:
                await query.message.edit_msg(
                    f"HTTP Exception for IMDB Search - <code>{exc}</code>"
                )
            except (MessageIdInvalid, MessageNotModified):
                pass
            except Exception as err:
                await query.message.edit_msg(
                    f"Failed when requesting movies title. Maybe got rate limit or down.\n\n<b>ERROR:</b> <code>{err}</code>"
                )


@app.on_cb("imdbres_id")
async def imdb_id_callback(self: Client, query: CallbackQuery):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Akses Ditolak!", True)
    with contextlib.redirect_stdout(sys.stderr):
        try:
            await query.message.edit_msg("⏳ Permintaan kamu sedang diproses.. ")
            imdb_url = f"https://m.imdb.com/title/tt{movie}/"
            resp = await fetch.get(imdb_url)
            resp.raise_for_status()
            sop = BeautifulSoup(resp, "lxml")
            r_json = json.loads(
                sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
            )
            ott = await search_jw(
                r_json.get("alternateName") or r_json.get("name"), "ID"
            )
            typee = r_json.get("@type", "")
            template = await get_imdb_template(query.from_user.id)
            hidden_fields = await _get_hidden_layout_fields(query.from_user.id)
            imdb_by = await get_imdb_by(query.from_user.id) or f"@{self.me.username}"
            res_str = ""
            duration_text = "-"
            duration_raw = "-"
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
            res_str += f"<b>📹 Judul:</b> <a href=\"{imdb_url}\">{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n"
            if aka := r_json.get("alternateName"):
                res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
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
            if kategori := r_json.get("contentRating"):
                category_text = kategori or "-"
                res_str += f"<b>Kategori:</b> <code>{kategori}</code> \n"
            rating_value = "-"
            rating_count = "-"
            if rating := r_json.get("aggregateRating"):
                rating_value = rating.get("ratingValue", "-")
                rating_count = rating.get("ratingCount", "-")
                res_str += f"<b>Peringkat:</b> <code>{rating_value}⭐️ dari {rating_count} pengguna</code>\n"
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
            if genre := r_json.get("genre"):
                genre_list = genre if isinstance(genre, list) else [genre]
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
            cast_lines = []
            director_names = []
            if directors := r_json.get("director"):
                director_names = [item["name"] for item in directors]
                director = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, " for i in directors
                )
                director_text = director[:-2] if director else "-"
                cast_lines.append(f"Sutradara: {director_text}")
                res_str += f"<b>Sutradara:</b> {director[:-2]}\n"
            writer_names = []
            if creators := r_json.get("creator"):
                writer_names = [
                    i["name"] for i in creators if i["@type"] == "Person"
                ]
                creator = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, "
                    for i in creators
                    if i["@type"] == "Person"
                )
                writer_text = creator[:-2] if creator else "-"
                cast_lines.append(f"Penulis: {writer_text}")
                res_str += f"<b>Penulis:</b> {creator[:-2]}\n"
            actor_names = []
            if actors := r_json.get("actor"):
                actor_names = [i["name"] for i in actors]
                actor = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, " for i in actors
                )
                cast_text = actor[:-2] if actor else "-"
                cast_lines.append(f"Pemeran: {cast_text}")
                res_str += f"<b>Pemeran:</b> {actor[:-2]}\n\n"
            cast_info = "\n".join(cast_lines) if cast_lines else "-"
            if deskripsi := r_json.get("description"):
                summary = (await gtranslate(deskripsi, "auto", "id")).text
                storyline_text = summary or "-"
                res_str += f"<b>📜 Plot:</b>\n<blockquote expandable><code>{summary}</code></blockquote>\n\n"
            keywords_list = []
            if keywd := r_json.get("keywords"):
                keywords_list = [kw.strip() for kw in keywd.split(",")]
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
                res_str += f"Tersedia di:\n{ott}\n"
            ott_text = ott
            if not ott_text:
                ott_text = "-"
            res_str += f"<b>©️ IMDb by</b> {imdb_by}"
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
                    "availability": ott_text,
                    "ott": ott_text,
                    "imdb_by": imdb_by,
                    "imdb_url": imdb_url,
                    "trailer_url": trailer_url,
                    "poster_url": poster_url,
                    "imdb_code": imdb_code,
                    "locale": "id",
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
                if "title" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>📹 Judul:</b> <a href=\"{imdb_url}\">{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n",
                        "",
                    )
                if "duration" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Durasi:</b> <code>{duration_text}</code>\n",
                        "",
                    )
                if "category" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Kategori:</b> <code>{category_text}</code> \n",
                        "",
                    )
                if "rating" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Peringkat:</b> <code>{rating_value}⭐️ dari {rating_count} pengguna</code>\n",
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
                    res_str = res_str.replace(f"Tersedia di:\n{ott}\n", "")
                if "imdb_by" in hidden_fields:
                    res_str = res_str.replace(f"<b>©️ IMDb by</b> {imdb_by}", "")
            if template:
                markup = template_markup
            else:
                if trailer := r_json.get("trailer"):
                    trailer_url = trailer["url"]
                    buttons = []
                    if "open_imdb" not in hidden_fields:
                        buttons.append(InlineKeyboardButton("🎬 Open IMDB", url=imdb_url))
                    if "trailer" not in hidden_fields:
                        buttons.append(
                            InlineKeyboardButton("▶️ Trailer", url=trailer_url)
                        )
                    markup = InlineKeyboardMarkup([buttons]) if buttons else None
                else:
                    if "open_imdb" in hidden_fields:
                        markup = None
                    else:
                        markup = InlineKeyboardMarkup(
                            [[InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)]]
                        )
            disable_web_preview = "web_preview" in hidden_fields
            send_as_photo = "send_as_photo" not in hidden_fields
            if not send_as_photo:
                await query.message.edit_msg(
                    res_str,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                    disable_web_page_preview=disable_web_preview,
                )
            elif thumb := r_json.get("image"):
                try:
                    await self.edit_message_media(
                        chat_id=query.message.chat.id,
                        message_id=query.message.id,
                        media=InputMediaPhoto(
                            thumb, caption=res_str, parse_mode=enums.ParseMode.HTML
                        ),
                        reply_markup=markup,
                    )
                except (PhotoInvalidDimensions, WebpageMediaEmpty):
                    poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                    await self.edit_message_media(
                        chat_id=query.message.chat.id,
                        message_id=query.message.id,
                        media=InputMediaPhoto(
                            poster, caption=res_str, parse_mode=enums.ParseMode.HTML
                        ),
                        reply_markup=markup,
                    )
                except (
                    MediaEmpty,
                    MediaCaptionTooLong,
                    WebpageCurlFailed,
                    MessageNotModified,
                ):
                    await query.message.edit_msg(
                        res_str,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=markup,
                        disable_web_page_preview=disable_web_preview,
                    )
                except Exception as err:
                    LOGGER.error(
                        f"Terjadi error saat menampilkan data IMDB. ERROR: {err}"
                    )
                    with contextlib.suppress(MessageNotModified, MessageIdInvalid):
                        await query.message.edit_msg(
                            res_str,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=markup,
                            disable_web_page_preview=disable_web_preview,
                        )
            else:
                await query.message.edit_msg(
                    res_str,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                    disable_web_page_preview=disable_web_preview,
                )
        except httpx.HTTPError as exc:
            await query.message.edit_msg(
                f"HTTP Exception for IMDB Search - <code>{exc}</code>"
            )
        except AttributeError:
            await query.message.edit_msg("Maaf, gagal mendapatkan info data dari IMDB.")
        except (MessageNotModified, MessageIdInvalid):
            pass


@app.on_cb("imdbres_en")
async def imdb_en_callback(self: Client, query: CallbackQuery):
    i, userid, movie = query.data.split("#")
    if query.from_user.id != int(userid):
        return await query.answer("⚠️ Access Denied!", True)
    with contextlib.redirect_stdout(sys.stderr):
        try:
            await query.message.edit_msg("<i>⏳ Getting IMDb source..</i>")
            imdb_url = f"https://m.imdb.com/title/tt{movie}/"
            resp = await fetch.get(imdb_url)
            resp.raise_for_status()
            sop = BeautifulSoup(resp, "lxml")
            r_json = json.loads(
                sop.find("script", attrs={"type": "application/ld+json"}).contents[0]
            )
            ott = await search_jw(
                r_json.get("alternateName") or r_json.get("name"), "US"
            )
            typee = r_json.get("@type", "")
            template = await get_imdb_template(query.from_user.id)
            hidden_fields = await _get_hidden_layout_fields(query.from_user.id)
            imdb_by = await get_imdb_by(query.from_user.id) or f"@{self.me.username}"
            res_str = ""
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
            rilis = "-"
            rilis_url = ""
            summary = ""
            tahun = (
                re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)[0]
                if re.findall(r"\d{4}\W\d{4}|\d{4}-?", sop.title.text)
                else "N/A"
            )
            res_str += f"<b>📹 Judul:</b> <a href=\"{imdb_url}\">{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n"
            if aka := r_json.get("alternateName"):
                res_str += f"<b>📢 AKA:</b> <code>{aka}</code>\n\n"
            else:
                res_str += "\n"
            if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
                durasi = (
                    durasi[0]
                    .find(class_="ipc-metadata-list-item__content-container")
                    .text
                )
                duration_raw = durasi
                duration_text = durasi
                res_str += f"<b>Duration:</b> <code>{durasi}</code>\n"
            if kategori := r_json.get("contentRating"):
                category_text = kategori or "-"
                res_str += f"<b>Category:</b> <code>{kategori}</code> \n"
            rating_value = "-"
            rating_count = "-"
            if rating := r_json.get("aggregateRating"):
                rating_value = rating.get("ratingValue", "-")
                rating_count = rating.get("ratingCount", "-")
                res_str += f"<b>Rating:</b> <code>{rating_value}⭐️ from {rating_count} users</code>\n"
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
            if genre := r_json.get("genre"):
                genre_list = genre if isinstance(genre, list) else [genre]
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
                res_str += f"<b>Country:</b> {country_text[:-2]}\n"
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
                res_str += f"<b>Language:</b> {language_text[:-2]}\n"
            if language_text == "-":
                language_text = "-"
            else:
                language_text = language_text[:-2]
            res_str += "\n<b>🙎 Cast Info:</b>\n"
            cast_lines = []
            director_names = []
            if r_json.get("director"):
                director_names = [item["name"] for item in r_json["director"]]
                director = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, "
                    for i in r_json["director"]
                )
                director_text = director[:-2] if director else "-"
                cast_lines.append(f"Director: {director_text}")
                res_str += f"<b>Director:</b> {director[:-2]}\n"
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
                cast_lines.append(f"Writer: {writer_text}")
                res_str += f"<b>Writer:</b> {creator[:-2]}\n"
            actor_names = []
            if r_json.get("actor"):
                actor_names = [i["name"] for i in r_json["actor"]]
                actors = actors = "".join(
                    f"<a href='{i['url']}'>{i['name']}</a>, " for i in r_json["actor"]
                )
                cast_text = actors[:-2] if actors else "-"
                cast_lines.append(f"Stars: {cast_text}")
                res_str += f"<b>Stars:</b> {actors[:-2]}\n\n"
            cast_info = "\n".join(cast_lines) if cast_lines else "-"
            if description := r_json.get("description"):
                storyline_text = description or "-"
                summary = description
                res_str += f"<b>📜 Summary:</b>\n<blockquote expandable><code>{description}</code></blockquote>\n\n"
            keywords_list = []
            if r_json.get("keywords"):
                keywords_list = [kw.strip() for kw in r_json["keywords"].split(",")]
                keyword_text = "".join(
                    f"#{i.replace(' ', '_').replace('-', '_')}, "
                    for i in keywords_list
                )
                res_str += (
                    f"<b>🔥 Keywords:</b>\n<blockquote expandable>{keyword_text[:-2]}</blockquote>\n"
                )
            if keyword_text != "-":
                keyword_text = keyword_text[:-2]
            if award := sop.select('li[data-testid="award_information"]'):
                awards = (
                    award[0]
                    .find(class_="ipc-metadata-list-item__list-content-item")
                    .text
                )
                awards_text = awards or "-"
                res_str += f"<b>🏆 Awards:</b>\n<blockquote expandable><code>{awards}</code></blockquote>\n"
            else:
                res_str += "\n"
            if ott != "":
                res_str += f"Available On:\n{ott}\n"
            if not ott:
                ott = "-"
            res_str += f"<b>©️ IMDb by</b> {imdb_by}"
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
                    rating_text = f"{rating_value}⭐️ from {rating_count} users"
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
                    "imdb_url": imdb_url,
                    "trailer_url": trailer_url,
                    "poster_url": poster_url,
                    "imdb_code": imdb_code,
                    "locale": "en",
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
                if "title" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>📹 Judul:</b> <a href=\"{imdb_url}\">{r_json.get('name')} [{tahun}]</a> (<code>{typee}</code>)\n",
                        "",
                    )
                if "duration" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Duration:</b> <code>{duration_text}</code>\n",
                        "",
                    )
                if "category" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Category:</b> <code>{category_text}</code> \n",
                        "",
                    )
                if "rating" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>Rating:</b> <code>{rating_value}⭐️ from {rating_count} users</code>\n",
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
                    res_str = res_str.replace(f"<b>Country:</b> {country_text}\n", "")
                if "language" in hidden_fields:
                    res_str = res_str.replace(f"<b>Language:</b> {language_text}\n", "")
                if "cast" in hidden_fields:
                    res_str = res_str.replace("\n<b>🙎 Cast Info:</b>\n", "")
                    res_str = res_str.replace(f"<b>Director:</b> {director_text}\n", "")
                    res_str = res_str.replace(f"<b>Writer:</b> {writer_text}\n", "")
                    res_str = res_str.replace(f"<b>Stars:</b> {cast_text}\n\n", "")
                if "storyline" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>📜 Summary:</b>\n<blockquote expandable><code>{summary}</code></blockquote>\n\n",
                        "",
                    )
                if "keyword" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>🔥 Keywords:</b>\n<blockquote expandable>{keyword_text}</blockquote>\n",
                        "",
                    )
                if "awards" in hidden_fields:
                    res_str = res_str.replace(
                        f"<b>🏆 Awards:</b>\n<blockquote expandable><code>{awards_text}</code></blockquote>\n",
                        "",
                    )
                if "ott" in hidden_fields:
                    res_str = res_str.replace(f"Available On:\n{ott}\n", "")
                if "imdb_by" in hidden_fields:
                    res_str = res_str.replace(f"<b>©️ IMDb by</b> {imdb_by}", "")
            if template:
                markup = template_markup
            else:
                if trailer := r_json.get("trailer"):
                    trailer_url = trailer["url"]
                    buttons = []
                    if "open_imdb" not in hidden_fields:
                        buttons.append(InlineKeyboardButton("🎬 Open IMDB", url=imdb_url))
                    if "trailer" not in hidden_fields:
                        buttons.append(
                            InlineKeyboardButton("▶️ Trailer", url=trailer_url)
                        )
                    markup = InlineKeyboardMarkup([buttons]) if buttons else None
                else:
                    if "open_imdb" in hidden_fields:
                        markup = None
                    else:
                        markup = InlineKeyboardMarkup(
                            [[InlineKeyboardButton("🎬 Open IMDB", url=imdb_url)]]
                        )
            disable_web_preview = "web_preview" in hidden_fields
            send_as_photo = "send_as_photo" not in hidden_fields
            if not send_as_photo:
                await query.message.edit_msg(
                    res_str,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                    disable_web_page_preview=disable_web_preview,
                )
            elif thumb := r_json.get("image"):
                try:
                    await self.edit_message_media(
                        chat_id=query.message.chat.id,
                        message_id=query.message.id,
                        media=InputMediaPhoto(
                            thumb, caption=res_str, parse_mode=enums.ParseMode.HTML
                        ),
                        reply_markup=markup,
                    )
                except (PhotoInvalidDimensions, WebpageMediaEmpty):
                    poster = thumb.replace(".jpg", "._V1_UX360.jpg")
                    await self.edit_message_media(
                        chat_id=query.message.chat.id,
                        message_id=query.message.id,
                        media=InputMediaPhoto(
                            poster, caption=res_str, parse_mode=enums.ParseMode.HTML
                        ),
                        reply_markup=markup,
                    )
                except (
                    MediaCaptionTooLong,
                    WebpageCurlFailed,
                    MediaEmpty,
                    MessageNotModified,
                ):
                    await query.message.edit_msg(
                        res_str,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=markup,
                        disable_web_page_preview=disable_web_preview,
                    )
                except Exception as err:
                    LOGGER.error(f"Error while displaying IMDB Data. ERROR: {err}")
                    with contextlib.suppress(MessageNotModified, MessageIdInvalid):
                        await query.message.edit_msg(
                            res_str,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=markup,
                            disable_web_page_preview=disable_web_preview,
                        )
            else:
                await query.message.edit_msg(
                    res_str,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                    disable_web_page_preview=disable_web_preview,
                )
        except httpx.HTTPError as exc:
            await query.message.edit_msg(
                f"HTTP Exception for IMDB Search - <code>{exc}</code>"
            )
        except AttributeError:
            await query.message.edit_msg("Sorry, failed getting data from IMDB.")
        except (MessageNotModified, MessageIdInvalid):
            pass
