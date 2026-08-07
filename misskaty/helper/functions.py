from copy import deepcopy
from datetime import datetime, timedelta
import re
from re import findall
from re import sub as re_sub
from string import ascii_lowercase

from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import BOT_USERNAME, app


def get_urls_from_text(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, text)]


def extract_urls(reply_markup):
    urls = []
    if reply_markup.inline_keyboard:
        buttons = reply_markup.inline_keyboard
        for i, row in enumerate(buttons):
            for j, button in enumerate(row):
                if button.url:
                    name = (
                        "\n~\nbutton"
                        if i * len(row) + j == 0
                        else f"button{i * len(row) + j + 1}"
                    )
                    urls.append((f"{name}", button.text, button.url))
    return urls




def has_button_markup(text: str | None) -> bool:
    if not text:
        return False
    return bool(
        re.search(r"\[[^\]]+\]\([^\)]+\)", text)
        or re.search(r"\[[^\],]+\s*,\s*[^\]]+\]", text)
    )


def _normalize_button_target(target: str, chat_id: int | None = None) -> str:
    target = target.strip()
    if target.startswith("#"):
        note_name = target[1:]
        return f"https://t.me/{BOT_USERNAME}?start=btnnotesm_{chat_id}_{note_name}" if chat_id else f"https://t.me/{BOT_USERNAME}?start={note_name}"

    if target.startswith(("http://", "https://", "tg://", "mailto:")):
        return target

    if re.match(r"^[\w.-]+\.[a-z]{2,}(?:[/:?#].*)?$", target, flags=re.I):
        return f"https://{target}"

    return target


def _parse_buttonurl_syntax(text: str, chat_id: int | None = None):
    rows = []
    current_row = []

    def _repl(match: re.Match):
        label = match.group(1).strip()
        raw_target = match.group(2).strip()
        if not raw_target.lower().startswith("buttonurl://"):
            return match.group(0)

        target = raw_target[len("buttonurl://") :]
        same_row = target.endswith(":same")
        if same_row:
            target = target[: -len(":same")]

        target = _normalize_button_target(target, chat_id=chat_id)
        if get_urls_from_text(target):
            btn = InlineKeyboardButton(text=label, url=target)
            if same_row and current_row:
                current_row.append(btn)
            else:
                if current_row:
                    rows.append(current_row.copy())
                    current_row.clear()
                current_row.append(btn)
        return ""

    cleaned = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", _repl, text)
    if current_row:
        rows.append(current_row.copy())
    return cleaned.strip(), (InlineKeyboardMarkup(rows) if rows else None)




async def _build_rules_button(message):
    from database.rules_db import get_rules_button

    if message.chat.username:
        label = await get_rules_button(message.chat.id)
        return InlineKeyboardButton(label, url=f"https://t.me/{message.chat.username}")
    return None


async def apply_fillings(text: str | None, message: Message, from_user, keyb: InlineKeyboardMarkup | None = None):
    text = text or ""
    first = from_user.first_name if getattr(from_user, "first_name", None) else ""
    last = from_user.last_name if getattr(from_user, "last_name", None) else ""
    fullname = " ".join([x for x in [first, last] if x]).strip()
    mention = from_user.mention if getattr(from_user, "mention", None) else fullname or "User"
    username = f"@{from_user.username}" if getattr(from_user, "username", None) else mention

    fillings = {
        "{first}": first,
        "{last}": last,
        "{fullname}": fullname or first or "-",
        "{username}": username,
        "{mention}": mention,
        "{id}": str(getattr(from_user, "id", "")),
        "{chatname}": message.chat.title or message.chat.first_name or "-",
    }

    for k, v in fillings.items():
        text = text.replace(k, v)

    send_opts = {
        "disable_notification": "{nonotif}" in text,
        "protect_content": "{protect}" in text,
        "media_spoiler": "{mediaspoiler}" in text,
        "preview": "{preview}" in text or "{preview:top}" in text,
        "preview_top": "{preview:top}" in text,
    }

    for token in ["{nonotif}", "{protect}", "{mediaspoiler}", "{preview}", "{preview:top}"]:
        text = text.replace(token, "")

    rules_new_row = "{rules}" in text
    rules_same_row = "{rules:same}" in text
    text = text.replace("{rules}", "").replace("{rules:same}", "")

    rules_btn = await _build_rules_button(message)
    if rules_btn:
        if keyb:
            rows = deepcopy(keyb.inline_keyboard)
            if rules_same_row and rows:
                rows[-1].append(rules_btn)
            elif rules_new_row:
                rows.append([rules_btn])
            keyb = InlineKeyboardMarkup(rows)
        elif rules_new_row or rules_same_row:
            keyb = InlineKeyboardMarkup([[rules_btn]])

    return text.strip(), keyb, send_opts


async def alpha_to_int(user_id_alphabet: str) -> int:
    alphabet = list(ascii_lowercase)[:10]
    user_id = ""
    for i in user_id_alphabet:
        index = alphabet.index(i)
        user_id += str(index)
    return int(user_id)


async def int_to_alpha(user_id: int) -> str:
    alphabet = list(ascii_lowercase)[:10]
    user_id = str(user_id)
    return "".join(alphabet[int(i)] for i in user_id)


async def extract_userid(message, text: str):
    """
    NOT TO BE USED OUTSIDE THIS FILE
    """

    def is_int(text: str):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()

    if is_int(text):
        return int(text)

    entities = message.entities
    if len(entities) < 2:
        return (await app.get_users(text)).id
    entity = entities[1]
    if entity.type == enums.MessageEntityType.MENTION:
        if entity.user:
            return entity.user.id
        return (await app.get_users(text)).id
    return None


async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None
    if message.reply_to_message:
        reply = message.reply_to_message
        # if reply to a message and no reason is given
        if reply.from_user:
            id_ = reply.from_user.id

        elif reply.sender_chat and reply.sender_chat != message.chat.id and sender_chat:
            id_ = reply.sender_chat.id
        else:
            return None, None
        reason = None if len(args) < 2 else text.split(None, 1)[1]
        return id_, reason

    # if not reply to a message and no reason is given
    if len(args) == 2:
        user = text.split(None, 1)[1]
        return await extract_userid(message, user), None

    # if reason is given
    if len(args) > 2:
        user, reason = text.split(None, 2)[1:]
        return await extract_userid(message, user), reason

    return user, reason


async def extract_user(message):
    return (await extract_user_and_reason(message))[0]


async def time_converter(time_value: str) -> datetime:
    """Convert ``1d`` / ``2h`` / ``30m`` to a datetime.

    Raises:
        ValueError: when the format is invalid or empty.
    """
    if not time_value or not time_value[:-1].isdigit():
        raise ValueError("Incorrect time specified")
    unit = ["m", "h", "d"]  # m == minutes | h == hours | d == days
    check_unit = "".join(filter(time_value[-1].lower().endswith, unit))
    currunt_time = datetime.now()
    time_digit = int(time_value[:-1])
    if time_digit <= 0:
        raise ValueError("Incorrect time specified")
    if check_unit == "m":
        return currunt_time + timedelta(minutes=time_digit)
    if check_unit == "h":
        return currunt_time + timedelta(hours=time_digit)
    if check_unit == "d":
        return currunt_time + timedelta(days=time_digit)
    raise ValueError("Incorrect time specified")


def extract_text_and_keyb(ikb, text: str, row_width: int = 2, chat_id: int | None = None):
    keyboard = {}
    try:
        text = text.strip()
        text = text.removeprefix("`")
        text = text.removesuffix("`")

        cleaned_text, parsed_keyboard = _parse_buttonurl_syntax(text, chat_id=chat_id)
        if parsed_keyboard:
            return cleaned_text, parsed_keyboard

        text, keyb = text.split("~")
        keyb = findall(r"\[.+\,.+\]", keyb)
        for btn_str in keyb:
            btn_str = re_sub(r"[\[\]]", "", btn_str)
            btn_str = btn_str.split(",")
            btn_txt, btn_url = btn_str[0], _normalize_button_target(btn_str[1].strip(), chat_id=chat_id)

            if not get_urls_from_text(btn_url):
                continue
            keyboard[btn_txt] = btn_url
        keyboard = ikb(keyboard, row_width)
    except Exception:
        return
    return text, keyboard
