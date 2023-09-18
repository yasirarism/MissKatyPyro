# * @author        Yasir Aris M <yasiramunandar@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   MissKatyPyro
# * Copyright ©YasirPedia All rights reserved
from logging import getLogger
from uuid import uuid4

from iytdl import Process, iYTDL, main
from iytdl.constants import YT_VID_URL
from iytdl.exceptions import DownloadFailedError
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    MessageEmpty,
    MessageIdInvalid,
    QueryIdInvalid,
    WebpageMediaEmpty,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from misskaty import app
from misskaty.core import pyro_cooldown
from misskaty.core.decorator import capture_err, new_task
from misskaty.helper import fetch, use_chat_lang
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL, SUDO

LOGGER = getLogger("MissKaty")
YT_REGEX = r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
YT_DB = {}


def rand_key():
    return str(uuid4())[:8]


@app.on_cmd("ytsearch", no_channel=True)
@use_chat_lang()
async def ytsearch(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply_msg(strings("no_query"))
    query = ctx.text.split(maxsplit=1)[1]
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
    await ctx.reply_photo(
        img, caption=caption, reply_markup=markup, parse_mode=ParseMode.HTML, quote=True
    )


@app.on_message(
    filters.command(["ytdown"], COMMAND_HANDLER)
    | filters.regex(YT_REGEX)
    & ~filters.channel
    & ~filters.via_bot
    & pyro_cooldown.wait(60)
)
@capture_err
@use_chat_lang()
async def ytdownv2(_, ctx: Message, strings):
    if not ctx.from_user:
        return await ctx.reply_msg(strings("no_channel"))
    if ctx.command and len(ctx.command) == 1:
        return await ctx.reply_msg(strings("invalid_link"))
    url = ctx.input if ctx.command and len(ctx.command) > 1 else ctx.text
    async with iYTDL(log_group_id=0, cache_path="cache", silent=True) as ytdl:
        try:
            x = await ytdl.parse(url, extract=True)
            if x is None:
                return await ctx.reply_msg(
                    strings("err_parse"), parse_mode=ParseMode.HTML
                )
            caption = x.caption
            markup = x.buttons
            photo = x.image_url
            try:
                await ctx.reply_photo(
                    photo,
                    caption=caption,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML,
                    quote=True,
                )
            except WebpageMediaEmpty:
                await ctx.reply_photo(
                    "assets/thumb.jpg",
                    caption=caption,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML,
                    quote=True,
                )
        except Exception as err:
            try:
                await ctx.reply_msg(str(err), parse_mode=ParseMode.HTML)
            except MessageEmpty:
                await ctx.reply("Invalid link.")


@app.on_cb(filters.regex(r"^yt_listall"))
@use_chat_lang()
async def ytdl_listall_callback(_, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer(strings("unauth"), True)
    callback = cq.data.split("|")
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/ffmpeg"
    ) as ytdl:
        media, buttons = await ytdl.listview(callback[1])
        await cq.edit_message_media(
            media=media, reply_markup=buttons.add(cq.from_user.id)
        )


@app.on_callback_query(filters.regex(r"^yt_extract_info"))
@use_chat_lang()
async def ytdl_extractinfo_callback(_, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        try:
            return await cq.answer(strings("unauth"), True)
        except QueryIdInvalid:
            return
    try:
        await cq.answer(strings("wait"))
    except QueryIdInvalid:
        pass
    callback = cq.data.split("|")
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/ffmpeg"
    ) as ytdl:
        try:
            if data := await ytdl.extract_info_from_key(callback[1]):
                if len(callback[1]) == 11:
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
        except Exception as e:
            await cq.edit_message_text(f"Extract Info Failed -> {e}")


@app.on_callback_query(filters.regex(r"^yt_(gen|dl)"))
@use_chat_lang()
@new_task
async def ytdl_gendl_callback(self: Client, cq: CallbackQuery, strings):
    if not (cq.message.reply_to_message and cq.message.reply_to_message.from_user):
        return
    match = cq.data.split("|")
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        try:
            return await cq.answer(strings("unauth"), True)
        except QueryIdInvalid:
            return
    if match[2] in ["mkv", "mp4"] and cq.from_user.id not in SUDO:
        try:
            return await cq.answer(strings("vip-btn"), True)
        except QueryIdInvalid:
            return await cq.delete()
    await cq.edit_message_caption("Downloading..")
    async with iYTDL(
        log_group_id=LOG_CHANNEL,
        cache_path="cache",
        ffmpeg_location="/usr/bin/ffmpeg",
        delete_media=True,
    ) as ytdl:
        try:
            if match[0] == "yt_gen":
                yt_url = False
                video_link = await ytdl.cache.get_url(match[1])
            else:
                yt_url = True
                video_link = f"{YT_VID_URL}{match[1]}"
            LOGGER.info(f"User {cq.from_user.id} using YTDL -> {video_link}")
            media_type = "video" if match[3] == "v" else "audio"
            uid, _ = ytdl.get_choice_by_id(match[2], media_type, yt_url=yt_url)
            key = await ytdl.download(
                url=video_link,
                uid=uid,
                downtype=media_type,
                update=cq,
            )
            await ytdl.upload(
                client=self,
                key=key[0],
                downtype=media_type,
                update=cq,
            )
        except DownloadFailedError as e:
            await cq.edit_message_caption(f"Download Failed - {e}")
        except Exception as err:
            try:
                await cq.edit_message_caption(
                    f"Download Failed for url -> {video_link}\n\n<b>ERROR:</b> <code>{err}</code>"
                )
            except MessageIdInvalid:
                pass


@app.on_callback_query(filters.regex(r"^yt_cancel"))
@use_chat_lang()
async def ytdl_cancel_callback(_, cq: CallbackQuery, strings):
    if cq.from_user.id != cq.message.reply_to_message.from_user.id:
        return await cq.answer(strings("unauth"), True)
    callback = cq.data.split("|")
    try:
        await cq.answer("Trying to Cancel Process..")
    except QueryIdInvalid:
        pass
    process_id = callback[1]
    try:
        Process.cancel_id(process_id)
        await cq.edit_message_caption("✔️ `Stopped Successfully`")
    except:
        return


@app.on_callback_query(filters.regex(r"^ytdl_scroll"))
@use_chat_lang()
async def ytdl_scroll_callback(_, cq: CallbackQuery, strings):
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
        if (await fetch.get(link)).status_code == 200:
            thumb_link = link
            break
    return thumb_link
