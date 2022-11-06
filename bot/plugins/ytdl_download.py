import os, logging, json, shutil, asyncio, time
from bot import app
from PIL import Image
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import COMMAND_HANDLER
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from bot.helper.ytdl_helper import random_char, DownLoadFile
from bot.helper.human_read import get_readable_file_size
from bot.plugins.dev import shell_exec
from bot.core.decorator.errors import capture_err
from bot.helper.pyro_progress import progress_for_pyrogram

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

user_time = {}

@app.on_message(filters.command(["ytdown"], COMMAND_HANDLER))
@capture_err
async def ytdown(_, message):
    if len(message.command) == 1:
        return await message.reply(f"Gunakan command /{message.command[0]} YT_LINK untuk download video dengan YT-DLP.")
    userLastDownloadTime = user_time.get(message.chat.id)
    try:
        if userLastDownloadTime > datetime.now():
            wait_time = round((userLastDownloadTime - datetime.now()).total_seconds() / 60, 2)
            await message.reply_text(f"Wait {wait_time} Minutes before next request..")
            return
    except:
        pass

    url = message.command[1]
    command_to_exec = f"yt-dlp --no-warnings --youtube-skip-dash-manifest -j {url}"
    t_response = (await shell_exec(command_to_exec))[0]
    if "ERROR" in t_response:
        await message.reply_text(
            text="No-one gonna help you\n<b>YT-DLP</b> said: {}".format(t_response),
            quote=True,
            disable_web_page_preview=True
        )
        return False
    if t_response:
        x_reponse = t_response
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        randem = random_char(5)
        if not os.path.exists("./YT_Down"):
            os.makedirs("./YT_Down")
        save_ytdl_json_path = f"YT_Down/{str(message.from_user.id)}{randem}.json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = formats.get("ext")

                if formats.get('filesize'):
                    size = formats['filesize']
                elif formats.get('filesize_approx'):
                    size = formats['filesize_approx']
                else:
                    size = 0
                cb_string_video = "ytdl|{}|{}|{}|{}".format(
                    "video", format_id, format_ext, randem)
                cb_string_file = "ytdl|{}|{}|{}|{}".format(
                    "file", format_id, format_ext, randem)
                if format_string and "audio only" not in format_string:
                    ikeyboard = [
                        InlineKeyboardButton(
                            "🎬 " + format_string + " " + format_ext +
                            " " + get_readable_file_size(size) + " ",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "📄 " + format_string + " " + format_ext +
                            " " + get_readable_file_size(size) + " ",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                else:
                    # special weird case :\
                    ikeyboard = [
                        InlineKeyboardButton(
                            "SVideo [" +
                            "] ( " +
                            get_readable_file_size(size) + " )",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "DFile [" +
                            "] ( " +
                            get_readable_file_size(size) + " )",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                inline_keyboard.append(ikeyboard)
            if duration is not None:
                cb_string_64 = "ytdl|{}|{}|{}|{}".format(
                    "audio", "64k", "mp3", randem)
                cb_string_128 = "ytdl|{}|{}|{}|{}".format(
                    "audio", "128k", "mp3", randem)
                cb_string = "ytdl|{}|{}|{}|{}".format(
                    "audio", "320k", "mp3", randem)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "MP3 " + "(" + "64 kbps" + ")",
                        callback_data=cb_string_64.encode("UTF-8")
                    ),
                    InlineKeyboardButton(
                        "MP3 " + "(" + "128 kbps" + ")",
                        callback_data=cb_string_128.encode("UTF-8")
                    )
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "MP3 " + "(" + "320 kbps" + ")",
                        callback_data=cb_string.encode("UTF-8")
                    )
                ])
        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "ytdl|{}|{}|{}|{}".format(
                "file", format_id, format_ext, randem)
            cb_string_video = "ytdl|{}|{}|{}|{}".format(
                "video", format_id, format_ext, randem)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "SVideo",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "DFile",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
            cb_string_file = "{}={}={}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}={}={}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "video",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "file",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        thumbnail = "https://uxwing.com/wp-content/themes/uxwing/download/signs-and-symbols/no-video-icon.png"
        thumbnail_image = "https://uxwing.com/wp-content/themes/uxwing/download/signs-and-symbols/no-video-icon.png"
        if "thumbnail" in response_json:
            if response_json["thumbnail"] is not None:
                thumbnail = response_json["thumbnail"]
                thumbnail_image = response_json["thumbnail"]
        thumb_image_path = DownLoadFile(
            thumbnail_image,
            f"YT_Down/{str(message.from_user.id)}{randem}.jpg",
            128,
            None,  # bot,
            "Trying to download..",
            message.id,
            message.chat.id
        )
        await message.reply_photo(
            photo=thumb_image_path,
            quote=True,
            caption="Select the desired format: <a href='{}'>file size might be approximate</a>".format(thumbnail),
            reply_markup=reply_markup,
        )
    else:
        # fallback for nonnumeric port a.k.a seedbox.io
        inline_keyboard = []
        cb_string_file = "{}={}={}".format(
            "file", "LFO", "NONE")
        cb_string_video = "{}={}={}".format(
            "video", "OFL", "ENON")
        inline_keyboard.append([
            InlineKeyboardButton(
                "SVideo",
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "DFile",
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await message.reply_photo(
            photo="https://telegra.ph/file/ce37f8203e1903feed544.png",
            quote=True,
            caption="Select the desired format: <a href='{}'>file size might be approximate</a>".format(""),
            reply_markup=reply_markup,
            reply_to_message_id=message.id
        )

@app.on_callback_query(filters.regex(r"ytdl|"))
async def youtube_dl_call_back(bot, update):
    cb_data = update.data
    usr = update.message.reply_to_message
    if update.from_user.id != usr.from_user.id:
        return await quer_y.answer("⚠️ Akses Denied!", True)
    # youtube_dl extractors
    _, tg_send_type, youtube_dl_format, youtube_dl_ext, ranom = cb_data.split("|")
    thumb_image_path = f"YT_Down/{str(update.from_user.id)}{ranom}.jpg"
    save_ytdl_json_path = f"YT_Down/{str(update.from_user.id)}{ranom}.json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except FileNotFoundError:
        await update.message.delete()
        return False

    custom_file_name = f"{str(response_json.get('title'))}_{youtube_dl_format}.{youtube_dl_ext}"
    youtube_dl_url = update.message.reply_to_message.text.split(" ", 1)[1]
    await update.message.edit_caption("Trying to download video...")
    description = " "
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][:1021] # escape Markdown and special characters
    tmp_directory_for_each_user = os.path.join(f"downloads/{str(update.from_user.id)}{random_char(5)}")
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = os.path.join(
        tmp_directory_for_each_user,
        custom_file_name
    )
    if tg_send_type == "audio":
        command_to_exec = f"yt-dlp -c --max-filesize 2097152000 --prefer-ffmpeg --extract-audio --audio-format {youtube_dl_ext} --audio-quality {youtube_dl_format} {youtube_dl_url} -o '{download_directory}'"
    else:
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = f"{youtube_dl_format}+bestaudio"
        command_to_exec = f"yt-dlp -c --max-filesize 2097152000 --embed-subs -f {minus_f_format} --hls-prefer-ffmpeg {youtube_dl_url} -o '{download_directory}'"
    start = datetime.now()
    t_response = (await shell_exec(command_to_exec))[0]
    LOGGER.info(download_directory)
    LOGGER.info(t_response)
    if t_response:
        os.remove(save_ytdl_json_path)
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        file_size = 2097152000 + 1
        download_directory_dirname = os.path.dirname(download_directory)
        download_directory_contents = os.listdir(download_directory_dirname)
        for download_directory_c in download_directory_contents:
            current_file_name = os.path.join(
                download_directory_dirname,
                download_directory_c
            )
            file_size = os.stat(current_file_name).st_size

            if file_size == 0:
                await update.message.edit(text="File Not found 🤒")
                asyncio.create_task(clendir(tmp_directory_for_each_user))
                return

            if file_size > 2097152000:
                await update.message.edit_caption(
                    caption="I cannot upload files greater than 1.95GB due to Telegram API limitations.".format(
                        time_taken_for_download,
                        humanbytes(file_size)
                    )
                )

            else:
                is_w_f = False
                await update.message.edit_caption(
                    caption="Trying to upload.."
                )
                # get the correct width, height, and duration
                # for videos greater than 10MB
                # ref: message from @BotSupport
                width = 0
                height = 0
                duration = 0
                if tg_send_type != "file":
                    metadata = extractMetadata(createParser(current_file_name))
                    if metadata is not None and metadata.has("duration"):
                        duration = metadata.get('duration').seconds
                # get the correct width, height, and duration
                # for videos greater than 10MB
                if os.path.exists(thumb_image_path):
                    # https://stackoverflow.com/a/21669827/4723940
                    Image.open(thumb_image_path).convert(
                        "RGB"
                    ).save(thumb_image_path)
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    if tg_send_type == "vm":
                        height = width
                else:
                    thumb_image_path = None
                start_time = time.time()
                # try to upload file
                if tg_send_type == "audio":
                    await update.message.reply_audio(
                        audio=current_file_name,
                        caption=description,
                        duration=duration,
                        thumb=thumb_image_path,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "Trying to upload...",
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "file":
                    await update.message.reply_document(
                        document=current_file_name,
                        thumb=thumb_image_path,
                        caption=description,
                        # reply_markup=reply_markup,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "Trying to upload...",
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "vm":
                    await update.message.reply_video_note(
                        video_note=current_file_name,
                        duration=duration,
                        length=width,
                        thumb=thumb_image_path,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "Trying to upload...",
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "video":
                    await update.message.reply_video(
                        video=current_file_name,
                        caption=description,
                        duration=duration,
                        width=width,
                        height=height,
                        supports_streaming=True,
                        thumb=thumb_image_path,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "Trying to upload...",
                            update.message,
                            start_time
                        )
                    )
                else:
                    LOGGER.info("Did this happen? :\\")
                end_two = datetime.now()
                time_taken_for_upload = (end_two - end_one).seconds
                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                except:
                    pass
                await update.message.edit_caption(
                    caption="Downloaded in {} seconds.\nUploaded in {} seconds.".format(
                        time_taken_for_download, time_taken_for_upload)

                )
                LOGGER.info(f"[OK] Downloaded in: {str(time_taken_for_download)}")
                LOGGER.info(f"[OK] Uploaded in: {str(time_taken_for_upload)}")
            shutil.rmtree(
                tmp_directory_for_each_user,
                ignore_errors=True
            )
            asyncio.create_task(clendir(thumb_image_path))
            asyncio.create_task(clendir(tmp_directory_for_each_user))
            await update.message.delete()


async def clendir(directory):
    try:
        shutil.rmtree(directory)
    except:
        pass
    try:
        os.remove(directory)
    except:
        pass