from re import compile as recompile
from logging import getLogger
from misskaty import app
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from pyrogram import filters
from iytdl import iYTDL, main
from uuid import uuid4

LOGGER = getLogger(__name__)
regex = recompile(
    r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
)
YT_DB = {}


def rand_key():
    return str(uuid4())[:8]


@app.on_message(filters.command(["ytsearch"], COMMAND_HANDLER) & ~filters.channel)
@capture_err
async def ytsearch(_, message):
    if len(message.command) == 1:
        return await message.reply("Please input a valid YT-DLP Supported URL")
    query = message.text.split(" ", maxsplit=1)[1]
    search_key = rand_key()
    YT_DB[search_key] = query
    search = await main.VideosSearch(query).next()
    if search["result"] == []:
        return await message.reply(f"No result found for `{query}`")
    i = search["result"][0]
    out = f"<b><a href={i['link']}>{i['title']}</a></b>"
    out += f"\nPublished {i['publishedTime']}\n"
    out += f"\n<b>❯ Duration:</b> {i['duration']}"
    out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
    out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
    btn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"1/{len(search['result'])}",
                    callback_data=f"ytdl_scroll|{search_key}|1",
                )
            ],
            [InlineKeyboardButton("Download", callback_data=f"yt_gen|{i['id']}")],
        ]
    )
    img = await get_ytthumb(i["id"])
    caption = out
    markup = btn
    await message.reply_photo(img, caption=caption, reply_markup=markup)


@app.on_message(filters.command(["ytdown2"], COMMAND_HANDLER) & ~filters.channel)
@capture_err
async def ytdownv2(_, message):
    if len(message.command) == 1:
        return await message.reply("Please input a valid YT-DLP Supported URL")
    url = message.text.split(" ", maxsplit=1)[1]
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/mediaextract"
    ) as ytdl:
        x = await ytdl.parse(url)
        img = await get_ytthumb(x.key)
        caption = x.caption
        markup = x.buttons
        await message.reply_photo(img, caption=caption, reply_markup=markup)


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
        if (await http.get(link)).status_code == 200:
            thumb_link = link
            break
    return thumb_link
