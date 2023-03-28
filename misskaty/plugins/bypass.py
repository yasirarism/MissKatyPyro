"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2022-12-01 09:32:31
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
import re
import urllib.parse
from urllib.parse import unquote

import requests
from pyrogram import filters
from pyrogram.errors import EntitiesTooLong, MessageTooLong
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.core.message_utils import *
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import http, get_readable_file_size, rentry
from misskaty.vars import COMMAND_HANDLER

LIST_LINK = """
- Pling and all aliases.
- Wetransfer
- Other link soon...
"""

__MODULE__ = "Bypass"
__HELP__ = f"""
/directurl [Link] - Bypass URL.

Supported Link:
{LIST_LINK}

Credit: <a href='https://github.com/sanjit-sinha/PyBypass'>PyBypass</a>
"""


async def pling_bypass(url):
    try:
        id_url = re.search(r"https?://(store.kde.org|www.pling.com)\/p\/(\d+)", url)[2]
        link = f"https://www.pling.com/p/{id_url}/loadFiles"
        res = await http.get(link)
        json_dic_files = res.json().pop("files")
        msg = f"\n**Source Link** :\n`{url}`\n**Direct Link :**\n"
        msg += "\n".join(f'**→ [{i["name"]}]({unquote(i["url"])}) ({get_readable_file_size(int(i["size"]))})**' for i in json_dic_files)
        return msg
    except Exception as e:
        return e


def wetransfer_bypass(url: str) -> str:
    if url.startswith("https://we.tl/"):
        r = requests.head(url, allow_redirects=True)
        url = r.url
    recipient_id = None
    params = urllib.parse.urlparse(url).path.split("/")[2:]

    if len(params) == 2:
        transfer_id, security_hash = params
    elif len(params) == 3:
        transfer_id, recipient_id, security_hash = params
    else:
        return None

    j = {
        "intent": "entire_transfer",
        "security_hash": security_hash,
    }

    if recipient_id:
        j["recipient_id"] = recipient_id
    try:
        s = requests.Session()
        r = s.get("https://wetransfer.com/")
        m = re.search('name="csrf-token" content="([^"]+)"', r.text)
        s.headers.update({"x-csrf-token": m[1], "x-requested-with": "XMLHttpRequest"})
        r = s.post(f"https://wetransfer.com/api/v4/transfers/{transfer_id}/download", json=j)
        j = r.json()
        dl_url = j["direct_link"]

        return f"\n**Source Link** :\n`{url}`\n**Direct Link :**\n{dl_url}"
    except Exception as er:
        return er


@app.on_message(filters.command(["directurl"], COMMAND_HANDLER))
@capture_err
@ratelimiter
async def bypass(_, message):
    if len(message.command) == 1:
        return await kirimPesan(message, f"Gunakan perintah /{message.command[0]} untuk bypass url")
    url = message.command[1]
    urllib.parse.urlparse(url).netloc
    msg = await kirimPesan(message, "Bypassing URL..", quote=True)
    mention = f"**Bypasser:** {message.from_user.mention} ({message.from_user.id})"
    if re.match(r"https?://(store.kde.org|www.pling.com)\/p\/(\d+)", url):
        data = await pling_bypass(url)
        try:
            await editPesan(msg, f"{data}\n\n{mention}")
        except (MessageTooLong, EntitiesTooLong):
            result = await rentry(data)
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Open Link", url=result),
                        InlineKeyboardButton("Raw Link", url=f"{result}/raw"),
                    ]
                ]
            )
            await editPesan(
                msg,
                f"{result}\n\nBecause your bypassed url is too long, so your link will be pasted to rentry.\n{mention}",
                reply_markup=markup,
                disable_web_page_preview=True,
            )
    else:
        data = wetransfer_bypass(url)
        await editPesan(msg, f"{data}\n\n{mention}")
