from asyncio import gather
from base64 import b64decode
from io import BytesIO
from pyrogram import filters
from misskaty import app
from info import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.http import post

__MODULE__ = "WebSS"
__HELP__ = """
/webss [URL] [FULL_SIZE?, use (y|yes|true) to get full size image. (optional)] - Take A Screenshot Of A Webpage.
"""


async def take_screenshot(url: str, full: bool = False):
    url = "https://" + url if not url.startswith("http") else url
    payload = {
        "url": url,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "format": "jpeg",
    }
    if full:
        payload["full"] = True
    data = await post(
        "https://webscreenshot.vercel.app/api",
        data=payload,
    )
    if "image" not in data:
        return None
    b = data["image"].replace("data:image/jpeg;base64,", "")
    file = BytesIO(b64decode(b))
    file.name = "webss.jpg"
    return file


@app.on_message(filters.command(["webss"], COMMAND_HANDLER))
@capture_err
async def take_ss(_, message):
    if len(message.command) < 2:
        return await message.reply("Give A Url To Fetch Screenshot.")

    if len(message.command) == 2:
        url = message.text.split(None, 1)[1]
        full = False
    elif len(message.command) == 3:
        url = message.text.split(None, 2)[1]
        full = message.text.split(None, 2)[2].lower().strip() in [
            "yes",
            "y",
            "1",
            "true",
        ]
    else:
        return await message.reply("Invalid Command.")

    m = await message.reply("Capturing screenshot...")

    try:
        photo = await take_screenshot(url, full)
        if not photo:
            return await m.edit("Failed To Take Screenshot")

        m = await m.edit("Uploading...")

        if not full:
            # Full size images have problem with reply_photo, that's why
            # we need to only use reply_photo if we're not using full size
            await gather(*[message.reply_document(photo), message.reply_photo(photo)])
        else:
            await message.reply_document(photo)
        await m.delete()
    except Exception as e:
        await m.edit(str(e))
