import logging
import os
import random
import string
from pathlib import Path

import httpx
import requests

from misskaty.helper.human_read import get_readable_file_size
from misskaty.vars import YT_COOKIES

LOGGER = logging.getLogger("MissKaty")


async def ensure_yt_cookies() -> None:
    """Download the YT cookies file once during startup (non-blocking).

    Uses a bounded timeout so a slow/unreachable URL can never stall the
    bot startup; on failure the bot simply runs without a cookie file.
    """
    if not YT_COOKIES:
        return
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(YT_COOKIES)
            if resp.status_code == 200:
                Path("cookies.txt").write_text(resp.text, encoding="utf-8")
                LOGGER.info("Success download YT Cookies")
            else:
                LOGGER.info("Failed download YT Cookies: status %s", resp.status_code)
    except Exception as exc:
        LOGGER.info("Failed download YT Cookies: %s", exc)


def random_char(y):
    return "".join(random.choice(string.ascii_letters) for _ in range(y))


def DetectFileSize(url):
    r = requests.get(url, allow_redirects=True, stream=True)
    return int(r.headers.get("content-length", 0))


def DownLoadFile(url, file_name, chunk_size, client, ud_type, message_id, chat_id):
    if os.path.exists(file_name):
        os.remove(file_name)
    if not url:
        return file_name
    r = requests.get(url, allow_redirects=True, stream=True)
    # https://stackoverflow.com/a/47342052/4723940
    total_size = int(r.headers.get("content-length", 0))
    downloaded_size = 0
    last_update = 0.0
    with open(file_name, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
                downloaded_size += len(chunk)
            if client is not None and total_size > 0 and downloaded_size > 0:
                progress = (downloaded_size * 100) // total_size
                if progress >= last_update + 5:
                    last_update = progress
                    try:
                        client.edit_message_text(
                            chat_id,
                            message_id,
                            text=f"{ud_type}: {get_readable_file_size(downloaded_size)} of {get_readable_file_size(total_size)}",
                        )
                    except Exception:
                        pass
    return file_name
