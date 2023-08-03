from datetime import datetime, timedelta
from re import findall
from re import sub as re_sub
from string import ascii_lowercase

from pyrogram import enums

from misskaty import app


def get_urls_from_text(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, text)]


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
        return (await app.get_users(text)).id
    if entity.type == enums.MessageEntityType.MENTION:
        return entity.user.id
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


async def time_converter(message, time_value: str) -> int:
    unit = ["m", "h", "d"]  # m == minutes | h == hours | d == days
    check_unit = "".join(list(filter(time_value[-1].lower().endswith, unit)))
    currunt_time = datetime.now()
    time_digit = time_value[:-1]
    if not time_digit.isdigit():
        return await message.reply_text("Incorrect time specified")
    if check_unit == "m":
        temp_time = currunt_time + timedelta(minutes=int(time_digit))
    elif check_unit == "h":
        temp_time = currunt_time + timedelta(hours=int(time_digit))
    elif check_unit == "d":
        temp_time = currunt_time + timedelta(days=int(time_digit))
    else:
        return await message.reply_text("Incorrect time specified.")
    return int(datetime.timestamp(temp_time))


def extract_text_and_keyb(ikb, text: str, row_width: int = 2):
    keyboard = {}
    try:
        text = text.strip()
        text = text.removeprefix("`")
        text = text.removesuffix("`")
        text, keyb = text.split("~")

        keyb = findall(r"\[.+\,.+\]", keyb)
        for btn_str in keyb:
            btn_str = re_sub(r"[\[\]]", "", btn_str)
            btn_str = btn_str.split(",")
            btn_txt, btn_url = btn_str[0], btn_str[1].strip()

            if not get_urls_from_text(btn_url):
                continue
            keyboard[btn_txt] = btn_url
        keyboard = ikb(keyboard, row_width)
    except Exception:
        return
    return text, keyboard
