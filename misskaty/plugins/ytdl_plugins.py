from logging import getLogger
from re import compile as recompile
from uuid import uuid4

from iytdl import iYTDL, main
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from misskaty import app
from misskaty.core.decorator.errors import capture_err
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper.http import http
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL

LOGGER = getLogger(__name__)
regex = recompile(
    r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
)
YT_DB = {}


def rand_key():
    return str(uuid4())[:8]


@app.on_message(filters.command(["ytsearch"], COMMAND_HANDLER) & ~filters.channel)
@capture_err
@ratelimiter
@use_chat_lang()
async def ytsearch(self: Client, ctx: Message, strings):
    if ctx.sender_chat:
        return await ctx.reply_msg(strings("no_channel"))
    if len(ctx.command) == 1:
        return await ctx.reply_msg(strings("no_query"))
    query = ctx.text.split(" ", maxsplit=1)[1]
    search_key = rand_key()
    YT_DB[search_key] = query
    search = await main.VideosSearch(query).next()
    if search["result"] == []:
        return await ctx.reply_msg(strings("no_res").format(kweri=query))
    i = search["result"][0]
    out = f"<b><a href={i['link']}>{i['title']}</a></b>\n"
    out = strings("yts_msg").format(
        pub=i["publishedTime"],
        dur=i["duration"],
        vi=i["viewCount"]["short"],
        clink=i["channel"]["link"],
        cname=i["channel"]["name"],
    )
    btn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"1/{len(search['result'])}",
                    callback_data=f"ytdl_scroll|{search_key}|1",
                )
            ],
            [
                InlineKeyboardButton(
                    strings("dl_btn"), callback_data=f"yt_gen|{i['id']}"
                )
            ],
        ]
    )
    img = await get_ytthumb(i["id"])
    caption = out
    markup = btn
    await ctx.reply_photo(img, caption=caption, reply_markup=markup, quote=True)


@app.on_message(filters.command(["ytdown"], COMMAND_HANDLER))
@capture_err
@ratelimiter
@use_chat_lang()
async def ytdownv2(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return await ctx.reply_msg(strings("no_channel"))
    if len(ctx.command) == 1:
        return await ctx.reply_msg(strings("invalid_link"))
    url = ctx.input
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/mediaextract"
    ) as ytdl:
        try:
            x = await ytdl.parse(url)
            if x is None:
                return await ctx.reply_msg(strings("err_parse"))
            img = await get_ytthumb(x.key)
            caption = x.caption
            markup = x.buttons
            await ctx.reply_photo(img, caption=caption, reply_markup=markup, quote=True)
        except Exception as err:
            await ctx.reply_msg(f"Opps, ERROR: {str(err)}")


@app.on_callback_query(filters.regex(r"^yt_listall"))
@ratelimiter
@use_chat_lang()
async def ytdl_listall_callback(self: Client, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer(strings("unauth"), True)
    callback = cq.data.split("|")
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/mediaextract"
    ) as ytdl:
        media, buttons = await ytdl.listview(callback[1])
        await cq.edit_message_media(
            media=media, reply_markup=buttons.add(cq.from_user.id)
        )


@app.on_callback_query(filters.regex(r"^yt_extract_info"))
@ratelimiter
@use_chat_lang()
async def ytdl_extractinfo_callback(self: Client, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer(strings("unauth"), True)
    await cq.answer(strings("wait"))
    callback = cq.data.split("|")
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/mediaextract"
    ) as ytdl:
        if data := await ytdl.extract_info_from_key(callback[1]):
            if len(key) == 11:
                await cq.edit_message_text(
                    text=data.caption,
                    reply_markup=data.buttons.add(cq.from_user.id),
                )
            else:
                await cq.edit_message_media(
                    media=(
                        InputMediaPhoto(
                            media=data.image_url,
                            caption=data.caption,
                        )
                    ),
                    reply_markup=data.buttons.add(cq.from_user.id),
                )


@app.on_callback_query(filters.regex(r"^yt_(gen|dl)"))
@ratelimiter
@use_chat_lang()
async def ytdl_gendl_callback(self: Client, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer(strings("unauth"), True)
    callback = cq.data.split("|")
    key = callback[1]
    if callback[0] == "yt_gen":
        if (
            match := regex.match(cq.message.reply_to_message.command[1])
            or len(callback) == 2
        ):
            x = await main.Extractor().get_download_button(key)
            await cq.edit_message_caption(caption=x.caption, reply_markup=x.buttons)
        else:
            uid = callback[2]
            type_ = callback[3]
            format_ = "audio" if type_ == "a" else "video"
            async with iYTDL(
                log_group_id=LOG_CHANNEL,
                cache_path="cache",
                ffmpeg_location="/usr/bin/mediaextract",
                delete_media=True,
            ) as ytdl:
                try:
                    upload_key = await ytdl.download(
                        cq.message.reply_to_message.command[1],
                        uid,
                        format_,
                        cq,
                        True,
                        3,
                    )
                    await ytdl.upload(app, upload_key[0], format_, cq, True)
                except Exception as err:
                    await cq.edit_message_caption(err)
    else:
        uid = callback[2]
        type_ = callback[3]
        format_ = "audio" if type_ == "a" else "video"
        async with iYTDL(
            log_group_id=LOG_CHANNEL,
            cache_path="cache",
            ffmpeg_location="/usr/bin/mediaextract",
            delete_media=True,
        ) as ytdl:
            try:
                upload_key = await ytdl.download(
                    f"https://www.youtube.com/watch?v={key}",
                    uid,
                    format_,
                    cq,
                    True,
                    3,
                )
                await ytdl.upload(app, upload_key[0], format_, cq, True)
            except Exception as err:
                await cq.edit_message_caption(err)


@app.on_callback_query(filters.regex(r"^ytdl_scroll"))
@ratelimiter
@use_chat_lang()
async def ytdl_scroll_callback(self: Client, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer(strings("unauth"), True)
    callback = cq.data.split("|")
    search_key = callback[1]
    page = int(callback[2])
    query = YT_DB[search_key]
    search = await main.VideosSearch(query).next()
    i = search["result"][page]
    out = f"<b><a href={i['link']}>{i['title']}</a></b>"
    out = strings("yts_msg").format(
        pub=i["publishedTime"],
        dur=i["duration"],
        vi=i["viewCount"]["short"],
        clink=i["channel"]["link"],
        cname=i["channel"]["name"],
    )
    scroll_btn = [
        [
            InlineKeyboardButton(
                strings("back"), callback_data=f"ytdl_scroll|{search_key}|{page-1}"
            ),
            InlineKeyboardButton(
                f"{page+1}/{len(search['result'])}",
                callback_data=f"ytdl_scroll|{search_key}|{page+1}",
            ),
        ]
    ]
    if page == 0:
        if len(search["result"]) == 1:
            return await cq.answer(strings("endlist"), show_alert=True)
        scroll_btn = [[scroll_btn.pop().pop()]]
    elif page == (len(search["result"]) - 1):
        scroll_btn = [[scroll_btn.pop().pop(0)]]
    btn = [[InlineKeyboardButton(strings("dl_btn"), callback_data=f"yt_gen|{i['id']}")]]
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
