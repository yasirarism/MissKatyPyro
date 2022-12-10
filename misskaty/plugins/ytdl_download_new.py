from re import compile as recompile
from logging import getLogger
from misskaty import app
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from pyrogram import filters
from iytdl import main
from uuid import uuid4

LOGGER = getLogger(__name__)
ytdl = main.iYTDL(LOG_CHANNEL, download_path="iytdl/", silent=True)
regex = recompile(
    r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
)
YT_DB = {}


@app.on_message(filters.command(["ytdown2"], COMMAND_HANDLER) & ~filters.channel)
@capture_err
async def ytdownv2(_, message):
    if len(message.command) == 1:
        return await message.reply("Please input a valid YT-DLP Supported URL")
    query = message.text.split(" ", maxsplit=1)[1]
    x = await ytdl.parse("https://fb.watch/heTbglEJ8O/", extract=True)
    y = await ytdl.parse("https://www.youtube.com/watch?v=VGt-BZ-SxGI")
    LOGGER.info(x)
    LOGGER.info(y)
    # img = await get_ytthumb(key)
    # caption = x.caption
    # markup = x.buttons
    # await message.reply_photo(img, caption=caption, reply_markup=markup)


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "maxresdefault.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if await http.get(link).status_code == 200:
            thumb_link = link
            break
    return thumb_link
