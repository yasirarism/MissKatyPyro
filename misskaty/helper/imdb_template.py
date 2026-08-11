"""Shared IMDB template rendering helpers.

Satu sumber kebenaran untuk render template layout IMDb yang dipakai oleh
plugin inline_search dan imdb_search. Sebelumnya diduplikasi di kedua plugin.
"""
import html
import logging
import re

from pyrogram.types import InlineKeyboardButton

LOGGER = logging.getLogger("MissKaty")


class ImdbTemplateDefaults(dict):
    """dict yang mengembalikan '-' untuk key yang tidak ada di payload."""

    def __missing__(self, key):
        return "-"


def _render_template_buttons(template: str, payload: dict):
    """Hapus tombol markdown `[label](url)` dari template, kumpulkan tombolnya.

    Mengembalikan (template_tanpa_tombol, list[InlineKeyboardButton]).
    """
    buttons = []

    def _replace(match: re.Match) -> str:
        label = match.group(1)
        url = match.group(2)
        try:
            label = label.format_map(ImdbTemplateDefaults(payload))
            url = url.format_map(ImdbTemplateDefaults(payload))
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
    """Render template menjadi teks HTML (tombol jadi anchor <a>)."""
    try:
        normalized = template.replace("\\n", "\n")
        rendered = normalized.format_map(ImdbTemplateDefaults(payload))
        return re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', rendered
        )
    except Exception as err:
        LOGGER.warning(f"Failed rendering IMDB template: {err}")
        return None


def render_imdb_template_with_buttons(template: str, payload: dict):
    """Render template; tombol markdown dikumpulkan sebagai tombol inline.

    Mengembalikan (rendered_text, list[InlineKeyboardButton]).
    """
    try:
        normalized = template.replace("\\n", "\n")
        template_without_buttons, buttons = _render_template_buttons(
            normalized, payload
        )
        rendered = template_without_buttons.format_map(ImdbTemplateDefaults(payload))
        return rendered, buttons
    except Exception as err:
        LOGGER.warning(f"Failed rendering IMDB template with buttons: {err}")
        return None, []


def _with_html_placeholders(payload: dict) -> dict:
    """Salin payload, tambahkan <key>_html berisi value yang di-escape HTML."""
    enriched = dict(payload)
    for key, value in payload.items():
        if value is None:
            value = "-"
        if isinstance(value, str):
            enriched[f"{key}_html"] = html.escape(value)
    return enriched


def normalize_imdb_layout_fields(stored_fields) -> set:
    """Normalisasi format field layout tersimpan menjadi set field tersembunyi."""
    if isinstance(stored_fields, dict):
        return {key for key, enabled in stored_fields.items() if not enabled}
    if isinstance(stored_fields, (list, tuple, set)):
        return set(stored_fields)
    return set()
