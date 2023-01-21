import os
import random
import string
import time
import json
import logging
from http.cookies import SimpleCookie
from urllib.parse import urlparse

import psutil

from misskaty import BOT_NAME, UBOT_NAME, botStartTime
from misskaty.helper.http import http
from misskaty.helper.human_read import get_readable_time
from misskaty.plugins import ALL_MODULES

LOGGER = logging.getLogger(__name__)

GENRES_EMOJI = {
    "Action": "👊",
    "Adventure": random.choice(["🪂", "🧗‍♀", "🌋"]),
    "Family": "👨‍",
    "Musical": "🎸",
    "Comedy": "🤣",
    "Drama": " 🎭",
    "Ecchi": random.choice(["💋", "🥵"]),
    "Fantasy": random.choice(["🧞", "🧞‍♂", "🧞‍♀", "🌗"]),
    "Hentai": "🔞",
    "History": "📜",
    "Horror": "☠",
    "Mahou Shoujo": "☯",
    "Mecha": "🤖",
    "Music": "🎸",
    "Mystery": "🔮",
    "Psychological": "♟",
    "Romance": "💞",
    "Sci-Fi": "🛸",
    "Slice of Life": random.choice(["☘", "🍁"]),
    "Sports": "⚽️",
    "Supernatural": "🫧",
    "Thriller": random.choice(["🥶", "🔪", "🤯"]),
}


async def bot_sys_stats():
    bot_uptime = int(time.time() - botStartTime)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    process = psutil.Process(os.getpid())
    return f"""
{UBOT_NAME}@{BOT_NAME}
------------------
UPTIME: {get_readable_time(bot_uptime)}
BOT: {round(process.memory_info()[0] / 1024**2)} MB
CPU: {cpu}%
RAM: {mem}%
DISK: {disk}%

TOTAL PLUGINS: {len(ALL_MODULES)}
"""


def get_random_string(length: int = 5):
    text_str = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))
    return text_str.upper()


async def rentry(teks):
    # buat dapetin cookie
    cookie = SimpleCookie()
    kuki = (await http.get("https://rentry.co")).cookies
    cookie.load(kuki)
    kukidict = {key: value.value for key, value in cookie.items()}
    # headernya
    header = {"Referer": "https://rentry.co"}
    payload = {"csrfmiddlewaretoken": kukidict["csrftoken"], "text": teks}
    return (
        (
            await http.post(
                "https://rentry.co/api/new",
                data=payload,
                headers=header,
                cookies=kukidict,
            )
        )
        .json()
        .get("url")
    )

def get_provider(url):

    def pretty(names):
        name = names[1]
        if names[0] == "play":
            name = "Google Play Movies"
        elif names[0] == "hbogoasia":
            name = "HBO Go Asia"
        elif names[0] == "maxstream":
            name = "Max Stream"
        elif names[0] == "klikfilm":
            name = "Klik Film"
        return name.title()

    netloc = urlparse(url).netloc
    return pretty(netloc.split('.'))

async def search_jw(movie_name: str, locale: str):
    m_t_ = ""
    try:
        response = (await http.get(f"https://yasirapi.eu.org/justwatch?q={movie_name}&locale={locale}")).json()
    except:
        return m_t_
    if not response.get("results"):
        LOGGER.error("JustWatch API Error or got Rate Limited.")
        return m_t_
    for item in response.get("results")["items"]:
        if movie_name == item.get("title", ""):
            offers = item.get("offers", [])
            t_m_ = []
            for offer in offers:
                url = offer.get("urls").get("standard_web")
                if url not in t_m_:
                    p_o = get_provider(url)
                    m_t_ += f"<a href='{url}'>{p_o}</a> | "
                t_m_.append(url)
            if m_t_ != "":
                m_t_ = m_t_[:-2].strip()
            break
    return m_t_
