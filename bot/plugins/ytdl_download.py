import os, logging, json
from bot import app
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import COMMAND_HANDLER
from datetime import datetime
from bot.helper.ytdl_helper import get_link, random_char
from bot.helper.human_read import get_readable_file_size
from bot.plugins.dev import shell_exec
from bot.core.decorator.errors import capture_err

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
    url, _, youtube_dl_username, youtube_dl_password = get_link(message)
    command_to_exec = f"yt-dlp --no-warnings --youtube-skip-dash-manifest -j {url}"
    t_response, e_response = await shell_exec(command_to_exec)
    LOGGER.info(await shell_exec(command_to_exec))
    # https://github.com/rg3/yt-dlp/issues/2630#issuecomment-38635239
    if e_response and "nonnumeric port" not in e_response:
        # logger.warn("Status : FAIL", exc.returncode, exc.output)
        error_message = e_response.replace(
            "Please report this issue on https://yt-dl.org/bug. Make sure you are using the latest version; see https://yt-dl.org/update on how to update. Be sure to call yt-dlp with the --verbose flag and include its complete output."
        )
        if "video is only available for registered users" in error_message:
            error_message += "This video only available for registered users."
        await update.reply_text(
            text="No-one gonna help you\n<b>YT-DLP</b> said: {}".format(str(error_message)),
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
        save_ytdl_json_path = "./YT_Down" + \
            "/" + str(update.from_user.id) + f'{randem}' + ".json"
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
                cb_string_video = "{}|{}|{}|{}".format(
                    "video", format_id, format_ext, randem)
                cb_string_file = "{}|{}|{}|{}".format(
                    "file", format_id, format_ext, randem)
                if format_string and "audio only" not in format_string:
                    ikeyboard = [
                        InlineKeyboardButton(
                            "🎬 " + format_string + " " + format_ext +
                            " " + humanbytes(size) + " ",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "📄 " + format_string + " " + format_ext +
                            " " + humanbytes(size) + " ",
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
                cb_string_64 = "{}|{}|{}|{}".format(
                    "audio", "64k", "mp3", randem)
                cb_string_128 = "{}|{}|{}|{}".format(
                    "audio", "128k", "mp3", randem)
                cb_string = "{}|{}|{}|{}".format(
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
            cb_string_file = "{}|{}|{}|{}".format(
                "file", format_id, format_ext, randem)
            cb_string_video = "{}|{}|{}|{}".format(
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
            "./YT_Down" + "/" +
            str(update.from_user.id) + f'{randem}' + ".jpg",
            128,
            None,  # bot,
            "Trying to download..",
            update.id,
            update.chat.id
        )
        await update.reply_photo(
            photo=thumb_image_path,
            quote=True,
            caption="Select the desired format: <a href='{}'>file size might be approximate</a>".format(
                thumbnail
            ) + "\n" + "If you want to download premium videos, provide in the following format:\n\nURL | filename | username | password",
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
        await update.reply_photo(
            photo="https://telegra.ph/file/ce37f8203e1903feed544.png",
            quote=True,
            caption="Select the desired format: <a href='{}'>file size might be approximate</a>".format(""),
            reply_markup=reply_markup,
            reply_to_message_id=update.id
        )