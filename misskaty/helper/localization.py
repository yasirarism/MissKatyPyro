import inspect
import json
import os.path
from functools import partial, wraps
from glob import glob
from typing import Dict, List

from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, InlineQuery, Message

from database.locale_db import get_db_lang

enabled_locales: List[str] = [
    # "en-GB",  # English (United Kingdom)
    "en-US",  # English (United States)
    "id-ID",  # Indonesian
    "id-JW",  # Javanese
]

default_language: str = "en-US"


def cache_localizations(files: List[str]) -> Dict[str, Dict[str, Dict[str, str]]]:
    ldict = {lang: {} for lang in enabled_locales}
    for file in files:
        _, lname, pname = file.split(os.path.sep)
        pname = pname.split(".")[0]
        dic = json.load(open(file, encoding="utf-8"))
        dic.update(ldict[lname].get(pname, {}))
        ldict[lname][pname] = dic
    return ldict


jsons: List[str] = []

for locale in enabled_locales:
    jsons += glob(os.path.join("locales", locale, "*.json"))

langdict = cache_localizations(jsons)


def get_locale_string(
    dic: dict, language: str, default_context: str, key: str, context: str = None
) -> str:
    if context:
        default_context = context
        dic = langdict[language].get(context, langdict[default_language][context])
    res: str = (
        dic.get(key) or langdict[default_language][default_context].get(key) or key
    )
    return res


async def get_lang(message) -> str:
    if isinstance(message, CallbackQuery):
        chat = message.message.chat
    elif isinstance(message, Message):
        chat = message.chat
    elif isinstance(message, InlineQuery):
        chat, chat.type = message.from_user, ChatType.PRIVATE
    else:
        raise TypeError(f"Update type '{message.__name__}' is not supported.")

    lang = await get_db_lang(chat.id)

    if chat.type == ChatType.PRIVATE:
        lang = lang or message.from_user.language_code or default_language
    else:
        lang = lang or default_language
    # User has a language_code without hyphen
    if len(lang.split("-")) == 1:
        # Try to find a language that starts with the provided language_code
        for locale_ in enabled_locales:
            if locale_.startswith(lang):
                lang = locale_
    elif lang.split("-")[1].islower():
        lang = lang.split("-")
        lang[1] = lang[1].upper()
        lang = "-".join(lang)
    return lang if lang in enabled_locales else default_language


def use_chat_lang(context: str = None):
    if not context:
        cwd = os.getcwd()
        frame = inspect.stack()[1]

        fname = frame.filename

        if fname.startswith(cwd):
            fname = fname[len(cwd) + 1 :]
        context = fname.split(os.path.sep)[2].split(".")[0]

    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            lang = await get_lang(message)

            dic = langdict.get(lang, langdict[default_language])

            lfunc = partial(get_locale_string, dic.get(context, {}), lang, context)
            return await func(client, message, lfunc)

        return wrapper

    return decorator
