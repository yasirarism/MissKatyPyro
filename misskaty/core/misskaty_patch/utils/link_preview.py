"""Kompatibilitas keyword lama Kurigram: `disable_web_page_preview`.

Kurigram 2.2.x menghapus `disable_web_page_preview` dari `send_message`, `reply_text`,
`edit_text`, dan `edit_message_text`; penggantinya `link_preview_options`
(:obj:`pyrogram.types.LinkPreviewOptions`). Plugin lama (dan docstring patch di repo ini)
masih memakai keyword lama, dan meneruskannya apa adanya ke fungsi pyrogram berakhir
``TypeError: got an unexpected keyword argument 'disable_web_page_preview'``.

Helper ini menormalkan kwargs sebelum diteruskan, sehingga keyword lama tetap didukung.
"""

from pyrogram.types import LinkPreviewOptions

LEGACY_KEY = "disable_web_page_preview"


def normalize_link_preview(kwargs: dict) -> dict:
    """Terjemahkan ``disable_web_page_preview`` menjadi ``link_preview_options``.

    Mengembalikan dict baru (kwargs asli tidak dimutasi) supaya aman dipakai ulang pada
    jalur retry. ``link_preview_options`` yang sudah diset eksplisit tidak ditimpa.
    """
    normalized = dict(kwargs)
    legacy = normalized.pop(LEGACY_KEY, None)

    if legacy is not None and normalized.get("link_preview_options") is None:
        normalized["link_preview_options"] = LinkPreviewOptions(is_disabled=bool(legacy))

    return normalized
