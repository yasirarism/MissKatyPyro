from misskaty.core.message_utils import *
from misskaty.vars import COMMAND_HANDLER
from pyrogram import filters
import cloudscraper, logging
from bot import app
from bs4 import BeautifulSoup
from pykeyboard import InlineButton, InlineKeyboard
from misskaty.helper import http
from misskaty.core.decorator.ratelimiter import ratelimiter

LOGGER = logging.getLogger(__name__)

@app.on_message(filters.command(["subscene"], COMMAND_HANDLER))
@ratelimiter
async def imdb_search_id(client, message):
    BTN = []
    if len(message.command) == 1:
        return await kirimPesan(message, f"ℹ️ Please add query after CMD!\nEx: <code>/{message.command[0]} Jurassic World</code>")
    if message.sender_chat:
        return await kirimPesan(message, "This feature not supported for channel..")
    kueri = message.text.split(None, 1)[1]
    k = await kirimPesan(
        message,
        f"🔎 Searching <code>{kueri}</code> Subscene database...",
        quote=True,
    )
    msg = ""
    buttons = InlineKeyboard(row_width=4)
    scraper = cloudscraper.create_scraper()
    try:
        param = {"query": kueri}
        r  = scraper.post("https://subscene.com/subtitles/searchbytitle", data=param).text
        soup = BeautifulSoup(r,"lxml")
        lists = soup.find("div", {"class": "search-result"})
        a = lists.find_all("div", {"class":"title"})
        LOGGER.info(a)
        # if not res:
        #     return await k.edit_caption(f"⛔️ No Result Found For: <code>{kueri}</code>")
        msg += f"🎬 Found ({len(a)}) result for : <code>{kueri}</code>\n\n"
        for num, sub in enumerate(a, start=1):
            title = sub.find('a').text
            url = f"https://subscene.com{sub.find('a').get('href')}"
            msg += f"{num}. <a href='{url}'>{title}</a>\n"
            BTN.append(
                InlineButton(
                    text=num,
                    callback_data=f"subscene#{message.from_user.id}#{title}",
                )
            )
        BTN.extend(
            (
                InlineButton(
                    text="❌ Close",
                    callback_data=f"close#{message.from_user.id}",
                ),
            )
        )
        buttons.add(*BTN)
        await editPesan(k, msg, reply_markup=buttons)
    except Exception as err:
        await editPesan(k, f"Ooppss, failed get subtitle list from subscene.\n\n<b>ERROR:</b> <code>{err}</code>")
