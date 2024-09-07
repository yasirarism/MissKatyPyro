"""
* @author        Yasir Aris M <yasiramunandar@gmail.com>
* @created       2022-12-01 09:12:27
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""
import privatebinapi
from json import loads as json_loads
from os import remove
from re import compile as compiles

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import app
from misskaty.helper import fetch, post_to_telegraph, rentry
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "Paste"
__HELP__ = """
/paste [Text/Reply To Message] - Post text to My Pastebin.
/sbin [Text/Reply To Message] - Post text to Spacebin.
/neko [Text/Reply To Message] - Post text to Nekobin.
/tgraph [Text/Reply To Message] - Post text to Telegraph.
/imgbb [Images] - Upload image to ImgBB.
/rentry [Text/Reply To Message] - Post text to Rentry using markdown style.
"""


# Size Checker for Limit
def humanbytes(size: int):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not isinstance(size, int):
        try:
            pass
        except ValueError:
            size = None
    if not size:
        return "0 B"
    size = int(size)
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {
        0: "",
        1: "K",
        2: "M",
        3: "G",
        4: "T",
        5: "P",
        6: "E",
        7: "Z",
        8: "Y",
    }
    while size > power:
        size /= power
        raised_to_pow += 1
    try:
        real_size = f"{str(round(size, 2))} {dict_power_n[raised_to_pow]}B"
    except KeyError:
        real_size = "Can't Define Real Size !"
    return real_size


# Pattern if extension supported, PR if want to add more
pattern = compiles(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$|x-subrip$")


@app.on_message(filters.command(["tgraph"], COMMAND_HANDLER))
async def telegraph_paste(_, message):
    reply = message.reply_to_message
    if not reply and len(message.command) < 2:
        return await message.reply_msg(
            f"**Reply To A Message With /{message.command[0]} or with command**",
            del_in=6,
        )

    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username} [{message.from_user.id}]"
        else:
            uname = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id}) [{message.from_user.id}]"
    else:
        uname = message.sender_chat.title
    msg = await message.reply_msg("`Pasting to Telegraph...`")
    data = ""
    limit = 1024 * 1024
    if reply and not (reply.text or reply.document):
        return await msg.edit_msg("**Telegraph upload has been disabled by Durov, use ImgBB command instead.**")
    if reply and reply.document:
        if reply.document.file_size > limit:
            return await msg.edit_msg(
                f"**You can only paste files smaller than {humanbytes(limit)}.**"
            )
        if not pattern.search(reply.document.mime_type):
            return await msg.edit_msg("**Only text files can be pasted.**")
        file = await reply.download()
        title = (
            message.text.split(None, 1)[1]
            if len(message.command) > 1
            else "MissKaty Paste"
        )
        try:
            with open(file, "r") as text:
                data = text.read()
            remove(file)
        except UnicodeDecodeError:
            try:
                remove(file)
            except:
                pass
            return await msg.edit_msg("`File Not Supported !`")
    elif reply and (reply.text or reply.caption):
        title = (
            message.text.split(None, 1)[1]
            if len(message.command) > 1
            else "MissKaty Paste"
        )
        data = reply.text.html.replace("\n", "<br>") or reply.caption.html.replace(
            "\n", "<br>"
        )
    elif not reply and len(message.command) >= 2:
        title = "MissKaty Paste"
        data = message.text.split(None, 1)[1]

    try:
        url = await post_to_telegraph(False, title, data)
    except Exception as e:
        return await msg.edit_msg(f"ERROR: {e}")

    if not url:
        return await msg.edit_msg("Text Too Short Or File Problems")
    button = [
        [InlineKeyboardButton("Open Link", url=url)],
        [
            InlineKeyboardButton(
                "Share Link", url=f"https://telegram.me/share/url?url={url}"
            )
        ],
    ]

    pasted = f"**Successfully pasted your data to Telegraph<a href='{url}'>.</a>\n\nPaste by {uname}**"
    await msg.edit_msg(pasted, reply_markup=InlineKeyboardMarkup(button))


@app.on_message(filters.command(["paste"], COMMAND_HANDLER))
async def wastepaste(_, message):
    reply = message.reply_to_message
    target = str(message.command[0]).split("@", maxsplit=1)[0]
    if not reply and len(message.command) < 2:
        return await message.reply_msg(
            f"**Reply To A Message With /{target} or with command**", del_in=6
        )

    msg = await message.reply_msg("`Pasting to YasirBin...`")
    data = ""
    limit = 1024 * 1024
    if reply and reply.document:
        if reply.document.file_size > limit:
            return await msg.edit_msg(
                f"**You can only paste files smaller than {humanbytes(limit)}.**"
            )
        if not pattern.search(reply.document.mime_type):
            return await msg.edit_msg("**Only text files can be pasted.**")
        file = await reply.download()
        try:
            with open(file, "r") as text:
                data = text.read()
            remove(file)
        except UnicodeDecodeError:
            try:
                remove(file)
            except:
                pass
            return await msg.edit_msg("`File Not Supported !`")
    elif reply and (reply.text or reply.caption):
        data = reply.text or reply.caption
    elif not reply and len(message.command) >= 2:
        data = message.text.split(None, 1)[1]

    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username} [{message.from_user.id}]"
        else:
            uname = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id}) [{message.from_user.id}]"
    else:
        uname = message.sender_chat.title

    try:
        url = await privatebinapi.send_async("https://bin.yasirweb.eu.org", text=data, expiration="1week", formatting="markdown")
    except Exception as e:
        return await msg.edit_msg(f"ERROR: {e}")

    if not url:
        return await msg.edit_msg("Text Too Short Or File Problems")
    button = [
        [InlineKeyboardButton("Open Link", url=url["full_url"])],
        [
            InlineKeyboardButton(
                "Share Link", url=f"https://telegram.me/share/url?url={url['full_url']}"
            )
        ],
    ]

    pasted = f"**Successfully pasted your data to YasirBin<a href='{url}'>.</a>\n\nPaste by {uname}**"
    await msg.edit_msg(pasted, reply_markup=InlineKeyboardMarkup(button))


# Nekobin Paste
@app.on_message(filters.command(["neko"], COMMAND_HANDLER))
async def nekopaste(_, message):
    reply = message.reply_to_message
    target = str(message.command[0]).split("@", maxsplit=1)[0]
    if not reply and len(message.command) < 2:
        return await message.reply_msg(
            f"**Reply To A Message With /{target} or with command**", del_in=6
        )

    msg = await message.reply_msg("`Pasting to Nekobin...`")
    data = ""
    limit = 1024 * 1024
    if reply and reply.document:
        if reply.document.file_size > limit:
            return await message.edit_msg(
                f"**You can only paste files smaller than {humanbytes(limit)}.**"
            )
        if not pattern.search(reply.document.mime_type):
            return await message.edit_msg("**Only text files can be pasted.**")
        file = await reply.download()
        try:
            with open(file, "r") as text:
                data = text.read()
            remove(file)
        except UnicodeDecodeError:
            try:
                remove(file)
            except:
                pass
            return await message.edit_msg("`File Not Supported !`")
    elif reply and (reply.text or reply.caption):
        data = reply.text.html or reply.caption.html
    elif not reply and len(message.command) >= 2:
        data = message.text.split(None, 1)[1]

    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username}"
        else:
            uname = (
                f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )
    else:
        uname = message.sender_chat.title

    try:
        x = (
            await fetch.post(
                "https://bin.mayuri.my.id/api/documents", json={"content": data}
            )
        ).json()
        url = f"https://bin.mayuri.my.id/{x['result']['key']}"
    except Exception as e:
        return await msg.edit_msg(f"ERROR: {e}")

    if not url:
        return await msg.edit_msg("Text Too Short Or File Problems")
    button = [
        [InlineKeyboardButton("Open Link", url=url)],
        [
            InlineKeyboardButton(
                "Share Link", url=f"https://telegram.me/share/url?url={url}"
            )
        ],
    ]

    pasted = f"**Successfully pasted your data to Nekobin<a href='{url}'>.</a>\n\nPaste by {uname}**"
    await msg.edit_msg(pasted, reply_markup=InlineKeyboardMarkup(button))


# Paste as spacebin
@app.on_message(filters.command(["sbin"], COMMAND_HANDLER))
async def spacebinn(_, message):
    reply = message.reply_to_message
    target = str(message.command[0]).split("@", maxsplit=1)[0]
    if not reply and len(message.command) < 2:
        return await message.reply_msg(
            f"**Reply To A Message With /{target} or with command**", del_in=6
        )

    msg = await message.reply_msg("`Pasting to Spacebin...`")
    data = ""
    limit = 1024 * 1024
    if reply and reply.document:
        if reply.document.file_size > limit:
            return await msg.edit_msg(
                f"**You can only paste files smaller than {humanbytes(limit)}.**"
            )
        if not pattern.search(reply.document.mime_type):
            return await msg.edit_msg("**Only text files can be pasted.**")
        file = await reply.download()
        try:
            with open(file, "r") as text:
                data = text.read()
            remove(file)
        except UnicodeDecodeError:
            try:
                remove(file)
            except:
                pass
            return await msg.edit_msg("`File Not Supported !`")
    elif reply and (reply.text or reply.caption):
        data = reply.text.html or reply.caption.html
    elif not reply and len(message.command) >= 2:
        data = message.text.split(None, 1)[1]

    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username}"
        else:
            uname = (
                f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )
    else:
        uname = message.sender_chat.title

    try:
        siteurl = "https://spaceb.in/api/"
        response = await fetch.post(siteurl, json={"content": data, "extension": "txt"})
        response = response.json()
        url = "https://spaceb.in/" + response["payload"]["id"]
    except Exception as e:
        return await msg.edit_msg(f"ERROR: {e}")

    if not url:
        return await msg.edit_msg("Text Too Short Or File Problems")
    button = [
        [InlineKeyboardButton("Open Link", url=url)],
        [
            InlineKeyboardButton(
                "Share Link", url=f"https://telegram.me/share/url?url={url}"
            )
        ],
    ]

    pasted = f"**Successfully pasted your data to Spacebin<a href='{url}'>.</a>\n\nPaste by {uname}**"
    await msg.edit_msg(pasted, reply_markup=InlineKeyboardMarkup(button))


# Rentry paste
@app.on_message(filters.command(["rentry"], COMMAND_HANDLER))
async def rentrypaste(_, message):
    reply = message.reply_to_message
    target = str(message.command[0]).split("@", maxsplit=1)[0]
    if not reply and len(message.command) < 2:
        return await message.reply_msg(
            f"**Reply To A Message With /{target} or with command**", del_in=6
        )

    msg = await message.reply_msg("`Pasting to Rentry...`")
    data = ""
    limit = 1024 * 1024
    if reply and reply.document:
        if reply.document.file_size > limit:
            return await msg.edit_msg(
                f"**You can only paste files smaller than {humanbytes(limit)}.**"
            )
        if not pattern.search(reply.document.mime_type):
            return await msg.edit_msg("**Only text files can be pasted.**")
        file = await reply.download()
        try:
            with open(file, "r") as text:
                data = text.read()
            remove(file)
        except UnicodeDecodeError:
            try:
                remove(file)
            except:
                pass
            return await msg.edit_msg("`File Not Supported !`")
    elif reply and (reply.text or reply.caption):
        data = reply.text.markdown or reply.caption.markdown
    elif not reply and len(message.command) >= 2:
        data = message.text.split(None, 1)[1]

    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username}"
        else:
            uname = (
                f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )
    else:
        uname = message.sender_chat.title

    try:
        url = await rentry(data)
    except Exception as e:
        return await msg.edit(f"`{e}`")

    if not url:
        return await msg.edit_msg("Text Too Short Or File Problems")
    button = [
        [InlineKeyboardButton("Open Link", url=url)],
        [
            InlineKeyboardButton(
                "Share Link", url=f"https://telegram.me/share/url?url={url}"
            )
        ],
    ]

    pasted = f"**Successfully pasted your data to Rentry<a href='{url}'>.</a>\n\nPaste by {uname}**"
    await msg.edit_msg(pasted, reply_markup=InlineKeyboardMarkup(button))


# ImgBB Upload
@app.on_message(filters.command(["imgbb"], COMMAND_HANDLER))
async def imgbb_upload(_, message):
    reply = message.reply_to_message
    if not reply and len(message.command) == 1:
        return await message.edit_msg(
            f"**Reply to a photo with /{message.command[0]} command to upload image on ImgBB.**", del_in=6
        )
    if not (reply.photo or (reply.document and reply.document.mime_type.startswith("image"))):
        return await message.reply_msg("This command only support upload photo")
    msg = await message.reply_msg("`Uploading image to ImgBB...`")
    if message.from_user:
        if message.from_user.username:
            uname = f"@{message.from_user.username}"
        else:
            uname = (
                f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )
    else:
        uname = message.sender_chat.title

    try:
        path = await reply.download()
        data = {"type": "file", "action": "upload"}
        files = {"source": (path, open(path, "rb"), "images/jpeg")}
        headers = {"origin": "https://imgbb.com", "referer": "https://imgbb.com/upload", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"}
        res = await fetch.post("https://imgbb.com/json", files=files, data=data, headers=headers)
        remove(path)
        url = f"https://ibb.co.com/{res.json()['image']['id_encoded']}"
        button = [
            [InlineKeyboardButton("Open Link", url=url)],
            [
                InlineKeyboardButton(
                    "Share Link", url=f"https://telegram.me/share/url?url={url}"
                )
            ],
        ]
    
        pasted = f"**Successfully pasted your images to ImgBB<a href='{url}'>.</a>\n\nPaste by {uname}**"
        await msg.edit_msg(pasted, reply_markup=InlineKeyboardMarkup(button))
    except Exception as e:
        await msg.edit_msg(f"ERROR: {e}")
