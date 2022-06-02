import re, heroku3
from os import environ

id_pattern = re.compile(r'^.\d+$')


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']
COMMAND_HANDLER = environ.get('COMMAND_HANDLER', '! /').split()

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))
PICS = (environ.get(
    'PICS',
    'https://telegra.ph/file/90e9a448bc2f8b055b762.jpg https://telegra.ph/file/e412e6ce9ca3ff0f7cef0.jpg https://telegra.ph/file/be3a1ed3f6fecfe6e114d.jpg https://telegra.ph/file/9d0e5c41406e15e1ee50e.jpg https://telegra.ph/file/afeddb3b69f3a4d2b228e.jpg https://telegra.ph/file/5e9097123d74bf37ce253.jpg https://telegra.ph/file/b72773f07bde54db42f8a.jpg https://telegra.ph/file/42760827e2894ca2ca493.jpg'
)).split()

# Admins, Channels & Users
ADMINS = [
    int(admin) if id_pattern.search(admin) else admin
    for admin in environ.get('ADMINS', '').split()
]
CHANNELS = [
    int(ch) if id_pattern.search(ch) else ch
    for ch in environ.get('CHANNELS', '0').split()
]
auth_users = [
    int(user) if id_pattern.search(user) else user
    for user in environ.get('AUTH_USERS', '').split()
]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(
    auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Rajappan")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'TeamEvamaria')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "False")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", None)
IMDB_TEMPLATE = environ.get(
    "IMDB_TEMPLATE",
    "<b>Query: {query}</b> \n‌‌‌‌IMDb Data:\n\n🏷 Title: <a href={url}>{title}</a>\n🎭 Genres: {genres}\n📆 Year: <a href={url}/releaseinfo>{year}</a>\n🌟 Rating: <a href={url}/ratings>{rating}</a> / 10"
)
LONG_IMDB_DESCRIPTION = is_enabled(
    environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
# Heroku Management
HEROKU_API_KEY = environ.get("HEROKU_API_KEY")
HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME")
HEROKU_APP = heroku3.from_key(HEROKU_API_KEY).apps(
)[HEROKU_APP_NAME] if HEROKU_API_KEY and HEROKU_APP_NAME else None

## Config For AUtoForwarder
# Forward From Chat ID
FORWARD_FROM_CHAT_ID = list(
    set(
        int(x) for x in environ.get(
            "FORWARD_FROM_CHAT_ID",
            "-1001128045651 -1001455886928 -1001686184174").split()))
# Forward To Chat ID
FORWARD_TO_CHAT_ID = list(
    set(
        int(x)
        for x in environ.get("FORWARD_TO_CHAT_ID", "-1001210537567").split()))
# Filters for Forwards
FORWARD_FILTERS = list(
    set(x for x in environ.get("FORWARD_FILTERS", "video document").split()))
BLOCKED_EXTENSIONS = list(
    set(x for x in environ.get(
        "BLOCKED_EXTENSIONS",
        "html htm json txt php gif png ink torrent url nfo xml xhtml jpg").
        split()))
MINIMUM_FILE_SIZE = environ.get("MINIMUM_FILE_SIZE", None)
BLOCK_FILES_WITHOUT_EXTENSIONS = bool(
    environ.get("BLOCK_FILES_WITHOUT_EXTENSIONS", True))
# Forward as Copy. Value Should be True or False
FORWARD_AS_COPY = bool(environ.get("FORWARD_AS_COPY", True))
# Sleep Time while Kang
SLEEP_TIME = int(environ.get("SLEEP_TIME", 10))