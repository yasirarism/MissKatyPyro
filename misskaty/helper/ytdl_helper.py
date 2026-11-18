import logging
import os
import random
import string
from html import escape
from pathlib import Path
from time import time

import httpx
import requests

from misskaty.helper.human_read import get_readable_file_size
from misskaty.helper.pyro_progress import humanbytes, time_formatter
from misskaty.vars import YT_COOKIES

LOGGER = logging.getLogger("MissKaty")

PROCESS_TEXT = "<emoji id=5319190934510904031>⏳</emoji> Processing.."


def format_progress_bar(percentage: float) -> str:
    filled = max(0, min(10, int(percentage // 10)))
    return f"[{'█' * filled}{'░' * (10 - filled)}]"


def _clean_line(text: str) -> str:
    return " ".join((text or "").split())


def _estimate_eta(state: dict) -> int:
    eta = int(state.get("eta") or 0)
    if eta > 0:
        return eta
    total = state.get("total") or 0
    speed = state.get("speed") or 0
    downloaded = state.get("downloaded") or 0
    if total > 0 and speed > 0 and downloaded < total:
        return int((total - downloaded) / speed)
    return 0


def dl_progress_text(state: dict, label: str, title: str, mention: str) -> str:
    total = state["total"]
    downloaded = min(state["downloaded"], total) if total else state["downloaded"]
    percentage = (downloaded / total * 100) if total else 0
    bar = format_progress_bar(percentage) if total else ""
    pct = f"{percentage:.1f}%" if total else "??%"
    speed = humanbytes(state["speed"]) or "0 B"
    eta_secs = _estimate_eta(state)
    eta = time_formatter(eta_secs).strip() if eta_secs else "Unknown"
    elapsed = time_formatter(int(time() - state.get("start", time()))).strip() or "0s"
    return (
        f"{PROCESS_TEXT}\n"
        "⬇️ Downloading\n"
        "<code>"
        f"🎬 {escape(_clean_line(title))[:60]}\n"
        f"{escape(_clean_line(label))}\n"
        f"{bar} {pct}\n"
        f"📦 {humanbytes(downloaded) or '0 B'} / {humanbytes(total) or '?'}\n"
        f"⚡ {speed}/s\n"
        f"⏱ Elapsed: {elapsed} • ETA: {eta}"
        "</code>\n"
        f"👤 {mention}"
    )


def dl_finalizing_text(label: str, mention: str) -> str:
    return (
        f"{PROCESS_TEXT}\n"
        "🧬 Finalizing\n"
        "<code>"
        f"🎞 {escape(_clean_line(label))}\n"
        "Merging & processing file..."
        "</code>\n"
        f"👤 {mention}"
    )


def dl_caption_meta(title: str, extra: list[str], mention: str) -> str:
    lines = ["<code>", f"🎬 {escape(_clean_line(title))}"]
    lines += [escape(_clean_line(x)) for x in extra if _clean_line(x)]
    lines += ["</code>", f"⬇️ Downloaded by {mention}"]
    return "\n".join(lines)


async def ensure_yt_cookies() -> None:
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
