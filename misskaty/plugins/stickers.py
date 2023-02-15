import asyncio
import os
import re
import shutil
import tempfile

from PIL import Image
from pyrogram import emoji, filters, enums
from pyrogram.errors import BadRequest, PeerIdInvalid, StickersetInvalid
from pyrogram.file_id import FileId
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet, RemoveStickerFromSet
from pyrogram.raw.types import DocumentAttributeFilename, InputDocument, InputMediaUploadedDocument, InputStickerSetItem, InputStickerSetShortName
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty import BOT_USERNAME, app
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper.http import http
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL

__MODULE__ = "Stickers"
__HELP__ = """
/kang [Reply to sticker] - Add sticker to your pack.
/unkang [Reply to sticker] - Remove sticker from your pack (Only can remove sticker that added by this bot.).
/getsticker - Convert sticker to png.
/stickerid - View sticker ID
"""


def get_emoji_regex():
    e_list = [getattr(emoji, e).encode("unicode-escape").decode("ASCII") for e in dir(emoji) if not e.startswith("_")]
    # to avoid re.error excluding char that start with '*'
    e_sort = sorted([x for x in e_list if not x.startswith("*")], reverse=True)
    # Sort emojis by length to make sure multi-character emojis are
    # matched first
    pattern_ = f"({'|'.join(e_sort)})"
    return re.compile(pattern_)


EMOJI_PATTERN = get_emoji_regex()
SUPPORTED_TYPES = ["jpeg", "png", "webp"]


@app.on_message(filters.command(["getsticker"], COMMAND_HANDLER))
@ratelimiter
async def getsticker_(c, m):
    if sticker := m.reply_to_message.sticker:
        if sticker.is_animated:
            await m.reply_text("Animated sticker is not supported!")
        else:
            with tempfile.TemporaryDirectory() as tempdir:
                path = os.path.join(tempdir, "getsticker")
            sticker_file = await c.download_media(
                message=m.reply_to_message,
                file_name=f"{path}/{sticker.set_name}.png",
            )
            await m.reply_to_message.reply_document(
                document=sticker_file,
                caption=(f"<b>Emoji:</b> {sticker.emoji}\n" f"<b>Sticker ID:</b> <code>{sticker.file_id}</code>\n\n" f"<b>Send by:</b> @{BOT_USERNAME}"),
            )
            shutil.rmtree(tempdir, ignore_errors=True)
    else:
        await m.reply_text("This is not a sticker!")


@app.on_message(filters.command("stickerid", COMMAND_HANDLER) & filters.reply)
@ratelimiter
async def getstickerid(c, m):
    if m.reply_to_message.sticker:
        await m.reply_text("The ID of this sticker is: <code>{stickerid}</code>".format(stickerid=m.reply_to_message.sticker.file_id))


@app.on_message(filters.command("unkang", COMMAND_HANDLER) & filters.reply)
@ratelimiter
async def getstickerid(c, m):
    if m.reply_to_message.sticker:
        pp = await m.reply_text("Trying to remove from pack..")
        try:
            decoded = FileId.decode(m.reply_to_message.sticker.file_id)
            sticker = InputDocument(
                id=decoded.media_id,
                access_hash=decoded.access_hash,
                file_reference=decoded.file_reference,
            )
            await app.invoke(RemoveStickerFromSet(sticker=sticker))
            await pp.edit("Sticker has been removed from your pack")
        except Exception as e:
            await pp.edit(f"Failed remove sticker from your pack.\n\nERR: {e}")
    else:
        await m.reply_text(f"Please reply sticker that created by {c.me.username} to remove sticker from your pack.")


@app.on_message(filters.command(["curi", "kang"], COMMAND_HANDLER))
@ratelimiter
async def kang_sticker(c, m):
    if not m.from_user:
        return await m.reply_text("You are anon admin, kang stickers in my pm.")
    prog_msg = await m.reply_text("Trying to steal your sticker...")
    sticker_emoji = "🤔"
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False
    reply = m.reply_to_message
    user = await c.resolve_peer(m.from_user.username or m.from_user.id)

    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.video:
            convert = True
            videos = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                # mime_type: image/webp
                resize = True
            elif reply.document.mime_type in (
                enums.MessageMediaType.VIDEO,
                enums.MessageMediaType.ANIMATION,
            ):
                # mime_type: application/video
                videos = True
                convert = True
            elif "tgsticker" in reply.document.mime_type:
                # mime_type: application/x-tgsticker
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit_text("The sticker has no name.")
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit_text()

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{m.from_user.id}_by_{c.me.username}"

        if len(m.command) > 1 and m.command[1].isdigit() and int(m.command[1]) > 0:
            # provide pack number to kang in desired pack
            packnum = m.command.pop(1)
            packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{c.me.username}"
        if len(m.command) > 1:
            # matches all valid emojis in input
            sticker_emoji = "".join(set(EMOJI_PATTERN.findall("".join(m.command[1:])))) or sticker_emoji
        filename = await c.download_media(m.reply_to_message)
        if not filename:
            # Failed to download
            await prog_msg.delete()
            return
    elif m.entities and len(m.entities) > 1:
        pack_prefix = "a"
        filename = "sticker.png"
        packname = f"c{m.from_user.id}_by_{c.me.username}"
        img_url = next(
            (m.text[y.offset : (y.offset + y.length)] for y in m.entities if y.type == "url"),
            None,
        )

        if not img_url:
            await prog_msg.delete()
            return
        try:
            r = await http.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
        if len(m.command) > 2:
            # m.command[1] is image_url
            if m.command[2].isdigit() and int(m.command[2]) > 0:
                packnum = m.command.pop(2)
                packname = f"a{packnum}_{m.from_user.id}_by_{c.me.username}"
            if len(m.command) > 2:
                sticker_emoji = "".join(set(EMOJI_PATTERN.findall("".join(m.command[2:])))) or sticker_emoji
            resize = True
    else:
        return await prog_msg.edit_text("Want me to guess the sticker?  Please tag a sticker.")
    try:
        if resize:
            filename = resize_image(filename)
        elif convert:
            filename = await convert_video(filename)
            if filename is False:
                return await prog_msg.edit_text("Error")
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await c.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = f"{pack_prefix}_{packnum}_{m.from_user.id}_by_{c.me.username}"
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await c.save_file(filename)
        media = await c.invoke(
            SendMedia(
                peer=(await c.resolve_peer(LOG_CHANNEL)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=c.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {m.from_user.id}",
                random_id=c.rnd_id(),
            ),
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document
        if packname_found:
            await prog_msg.edit_text("<code>Using existing sticker pack...</code>")
            await c.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit_text("<b>Creating a new sticker pack...</b>")
            stkr_title = f"{m.from_user.first_name}'s"
            if animated:
                stkr_title += "AnimPack"
            elif videos:
                stkr_title += "VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await c.invoke(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        animated=animated,
                        videos=videos,
                    )
                )
            except PeerIdInvalid:
                return await prog_msg.edit_text(
                    "It looks like you've never interacted with me in private chat, you need to do that first..",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Click Me",
                                    url=f"https://t.me/{c.me.username}?start",
                                )
                            ]
                        ]
                    ),
                )

    except BadRequest:
        return await prog_msg.edit_text("Your Sticker Pack is full if your pack is not in v1 Type /kang 1, if it is not in v2 Type /kang 2 and so on.")
    except Exception as all_e:
        await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="👀 View Your Pack",
                        url=f"https://t.me/addstickers/{packname}",
                    )
                ]
            ]
        )
        await prog_msg.edit_text(
            f"<b>Sticker successfully stolen!</b>\n<b>Emoji:</b> {sticker_emoji}",
            reply_markup=markup,
        )
        # Cleanup
        await c.delete_messages(chat_id=LOG_CHANNEL, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass


def resize_image(filename: str) -> str:
    im = Image.open(filename)
    maxsize = 512
    scale = maxsize / max(im.width, im.height)
    sizenew = (int(im.width * scale), int(im.height * scale))
    im = im.resize(sizenew, Image.NEAREST)
    downpath, f_name = os.path.split(filename)
    # not hardcoding png_image as "sticker.png"
    png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
    im.save(png_image, "PNG")
    if png_image != filename:
        os.remove(filename)
    return png_image


async def convert_video(filename: str) -> str:
    downpath, f_name = os.path.split(filename)
    webm_video = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.webm")
    cmd = [
        "mediaextract",
        "-loglevel",
        "quiet",
        "-i",
        filename,
        "-t",
        "00:00:03",
        "-vf",
        "fps=30",
        "-c:v",
        "vp9",
        "-b:v:",
        "500k",
        "-preset",
        "ultrafast",
        "-s",
        "512x512",
        "-y",
        "-an",
        webm_video,
    ]

    proc = await asyncio.create_subprocess_exec(*cmd)
    # Wait for the subprocess to finish
    await proc.communicate()

    if webm_video != filename:
        os.remove(filename)
    return webm_video
