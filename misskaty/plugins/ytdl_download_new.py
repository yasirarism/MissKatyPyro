from re import compile as recompile
from logging import getLogger
from misskaty import app
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import http
from pyrogram import filters
from iytdl import iYTDL
from uuid import uuid4

LOGGER = getLogger(__name__)
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
    async with iYTDL(
        log_group_id=0, cache_path="cache", ffmpeg_location="/usr/bin/mediaextract"
    ) as ytdl:
        x = await ytdl.parse("https://www.youtube.com/watch?v=VGt-BZ-SxGI")
        img = x.image_url
        caption = x.caption
        markup = x.buttons
        await message.reply_photo(img, caption=caption, reply_markup=markup)
