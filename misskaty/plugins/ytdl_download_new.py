from re import compile as recompile
from logging import getLogger
from misskaty import app
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    InputMediaPhoto,
)
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
        return await message.reply("Please input a query..!")
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
    await message.reply_photo(img, caption=caption, reply_markup=markup, quote=True)


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
        await message.reply_photo(img, caption=caption, reply_markup=markup, quote=True)


@app.on_callback_query(filters.regex(r"^yt_(gen|dl)"))
async def ytdl_gendl_callback(_, cq: CallbackQuery):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer("Not your task", True)
    callback = cq.data.split("|")
    key = callback[1]
    if callback[0] == "yt_gen":
        x = await main.Extractor().get_download_button(key)
        await cq.edit_message_caption(caption=x.caption, reply_markup=x.buttons)
    else:
        uid = callback[2]
        type_ = callback[3]
        if type_ == "a":
            format_ = "audio"
        else:
            format_ = "video"
        async with iYTDL(
            log_group_id=LOG_CHANNEL,
            cache_path="cache",
            ffmpeg_location="/usr/bin/mediaextract",
            delete_media=True,
        ) as ytdl:
            upload_key = await ytdl.download(
                cq.message.reply_to_message.command[1], uid, format_, cq, True, 3
            )
            await ytdl.upload(app, upload_key, format_, cq, True)


@app.on_callback_query(filters.regex(r"^ytdl_scroll"))
async def ytdl_scroll_callback(_, cq: CallbackQuery):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer("Not your task", True)
    callback = cq.data.split("|")
    search_key = callback[1]
    page = int(callback[2])
    query = YT_DB[search_key]
    search = await main.VideosSearch(query).next()
    i = search["result"][page]
    out = f"<b><a href={i['link']}>{i['title']}</a></b>"
    out += f"\nPublished {i['publishedTime']}\n"
    out += f"\n<b>❯ Duration:</b> {i['duration']}"
    out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
    out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
    scroll_btn = [
        [
            InlineKeyboardButton(
                f"Back", callback_data=f"ytdl_scroll|{search_key}|{page-1}"
            ),
            InlineKeyboardButton(
                f"{page+1}/{len(search['result'])}",
                callback_data=f"ytdl_scroll|{search_key}|{page+1}",
            ),
        ]
    ]
    if page == 0:
        if len(search["result"]) == 1:
            return await cq.answer("That's the end of list", show_alert=True)
        scroll_btn = [[scroll_btn.pop().pop()]]
    elif page == (len(search["result"]) - 1):
        scroll_btn = [[scroll_btn.pop().pop(0)]]
    btn = [[InlineKeyboardButton("Download", callback_data=f"yt_gen|{i['id']}")]]
    btn = InlineKeyboardMarkup(scroll_btn + btn)
    await cq.edit_message_media(
        InputMediaPhoto(await get_ytthumb(i["id"]), caption=out), reply_markup=btn
    )


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
