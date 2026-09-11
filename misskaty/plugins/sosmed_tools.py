import asyncio
import contextlib
import math
import os
import time
from datetime import datetime
from logging import getLogger
from urllib.parse import unquote
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram import types as pyro_types
from pyrogram.file_id import FileId
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
)
from pySmartDL import SmartDL
from misskaty import app
from misskaty.core.decorator import capture_err, new_task
from misskaty.helper.http import fetch
from misskaty.helper.pyro_progress import humanbytes, progress_for_pyrogram
from misskaty.helper.sosmed_helper import (
    ACTIVE_TG_DOWNLOADS,
    _build_plain_card,
    _build_rich_card,
    _esc,
    _fb_keyboard,
    _fb_plain_card,
    _fb_rich_card,
    _get_facebook_data,
    _get_instagram_data,
    _get_tiktok_data,
    _tg_download_cancel_markup,
    _tg_download_progress,
    _tt_keyboard,
    _tt_plain_card,
    _tt_rich_card,
    _url_keyboard,
)
from misskaty.vars import COMMAND_HANDLER, OWNER_ID


LOGGER = getLogger("MissKaty")


__MODULE__ = "SosmedTools"


__HELP__ = """
/igdl [link] atau /instadl [link] - Instagram post/reel sebagai slideshow rich message (media, likes, komentar, caption, metadata video).
/tiktokdl [link] - TikTok video/foto sebagai slideshow rich message (alias: /ttdl).
/fbdl [link] - Facebook post/reel/video sebagai slideshow rich message.
  Metrik (reaksi/komentar/share) butuh cookies.txt akun Facebook.
/twitterdl [link] - Download video dari Twitter/X.
/ytdown [YT-DLP URL] - Download video/audio via yt-dlp.
/download [url] atau reply file - Download ke server (OWNER only).
/anon [reply file] - Upload file ke anonfiles.
"""


@app.on_message(filters.command(["anon"], COMMAND_HANDLER))
async def upload(bot, message):
    if not message.reply_to_message:
        return await message.reply("Please reply to media file.")
    vid = [
        message.reply_to_message.video,
        message.reply_to_message.document,
        message.reply_to_message.audio,
        message.reply_to_message.photo,
    ]
    media = next((v for v in vid if v is not None), None)
    if not media:
        return await message.reply("Unsupported media type..")
    m = await message.reply("Download your file to my Server...")
    now = time.time()
    dc_id = FileId.decode(media.file_id).dc_id
    fileku = await message.reply_to_message.download(
        progress=progress_for_pyrogram,
        progress_args=("Trying to download, please wait..", m, now, dc_id),
    )
    try:
        files = {"file": open(fileku, "rb")}
        await m.edit("Uploading to Anonfile, Please Wait||")
        callapi = await fetch.post("https://api.anonfiles.com/upload", files=files)
        text = callapi.json()
        output = f'<u>File Uploaded to Anonfile</u>\n\n📂 File Name: {text["data"]["file"]["metadata"]["name"]}\n\n📦 File Size: {text["data"]["file"]["metadata"]["size"]["readable"]}\n\n📥 Download Link: {text["data"]["file"]["url"]["full"]}'

        btn = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 Download 📥", url=f"{text['data']['file']['url']['full']}"
                    )
                ]
            ]
        )
        await m.edit(output, reply_markup=btn)
    except Exception as e:
        await bot.send_message(message.chat.id, text=f"Something Went Wrong!\n\n{e}")
    os.remove(fileku)


@app.on_message(filters.command(["download"], COMMAND_HANDLER) & filters.user(OWNER_ID))
@capture_err
@new_task
async def download(client, message):
    pesan = await message.reply_text("<emoji id=5319190934510904031>⏳</emoji> Processing..")
    if message.reply_to_message is not None:
        start_t = datetime.now()
        c_time = time.time()
        vid = [
            message.reply_to_message.video,
            message.reply_to_message.document,
            message.reply_to_message.audio,
            message.reply_to_message.photo,
        ]
        media = next((v for v in vid if v is not None), None)
        if not media:
            return await pesan.edit("Unsupported media type..")
        dc_id = FileId.decode(media.file_id).dc_id
        job_id = f"{message.chat.id}:{pesan.id}"
        user_id = message.from_user.id if message.from_user else OWNER_ID
        await pesan.edit(
            f"<emoji id=5319190934510904031>⏳</emoji> Downloading Telegram file...\nDC ID: {dc_id}",
            reply_markup=_tg_download_cancel_markup(job_id, user_id),
        )
        download_task = asyncio.create_task(
            client.download_media(
                message=message.reply_to_message,
                progress=_tg_download_progress,
                progress_args=("Trying to download, sabar yakk..", pesan, c_time, dc_id, job_id, user_id),
            )
        )
        ACTIVE_TG_DOWNLOADS[job_id] = {"task": download_task, "user_id": user_id}
        try:
            the_real_download_location = await download_task
        except asyncio.CancelledError:
            ACTIVE_TG_DOWNLOADS.pop(job_id, None)
            with contextlib.suppress(Exception):
                await pesan.edit("❌ Download cancelled.")
            return
        ACTIVE_TG_DOWNLOADS.pop(job_id, None)
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await pesan.edit(
            f"Downloaded to <code>{the_real_download_location}</code> in <u>{ms}</u> seconds."
        )
    elif len(message.command) > 1:
        start_t = datetime.now()
        the_url_parts = " ".join(message.command[1:])
        url = the_url_parts.strip()
        custom_file_name = os.path.basename(url)
        if "|" in the_url_parts:
            url, custom_file_name = the_url_parts.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()
        download_file_path = os.path.join("downloads/", custom_file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False, timeout=10)
        try:
            downloader.start(blocking=False)
        except Exception as err:
            return await message.edit(str(err))
        c_time = time.time()
        while not downloader.isFinished():
            total_length = downloader.filesize or None
            downloaded = downloader.get_dl_size(human=True)
            display_message = ""
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed(human=True)
            progress_str = "[{0}{1}]\nProgress: {2}%".format(
                "".join(["●" for _ in range(math.floor(percentage / 5))]),
                "".join(["○" for _ in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )

            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = "<emoji id=5319190934510904031>⏳</emoji> Processing..\n"
                current_message += f"URL: <code>{url}</code>\n"
                current_message += (
                    f"File Name: <code>{unquote(custom_file_name)}</code>\n"
                )
                current_message += f"Speed: {speed}\n"
                current_message += f"{progress_str}\n"
                current_message += f"{downloaded} of {humanbytes(total_length)}\n"
                current_message += f"ETA: {estimated_total_time}"
                if round(diff % 10.00) == 0 and current_message != display_message:
                    await pesan.edit(
                        link_preview_options=pyro_types.LinkPreviewOptions(is_disabled=True), text=current_message
                    )
                    display_message = current_message
                    await asyncio.sleep(10)
            except Exception as e:
                LOGGER.info(str(e))
        if os.path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await pesan.edit(
                f"Downloaded to <code>{download_file_path}</code> in {ms} seconds"
            )
    else:
        await pesan.edit(
            "Reply to a Telegram Media, to download it to my local server."
        )


@app.on_callback_query(filters.regex(r"^tgdl_cancel#"))
async def tg_download_cancel(_, query):
    try:
        _, job_id, user_id = (query.data or "").split("#", 2)
    except ValueError:
        return await query.answer("Invalid task", True)
    if query.from_user.id != int(user_id):
        return await query.answer("Not yours!", True)
    job = ACTIVE_TG_DOWNLOADS.get(job_id)
    if not job:
        return await query.answer("Task already finished", True)
    task = job.get("task")
    if task and not task.done():
        task.cancel()
    await query.answer("Cancelling download...")


@app.on_message(filters.command(["igdl", "instadl"], COMMAND_HANDLER))
@capture_err
async def igdl_handler(client, message):
    if len(message.command) == 1:
        return await message.reply(
            f"<b>📸 Instagram Downloader</b>\n\n"
            f"Gunakan: <code>/{message.command[0]} &lt;link&gt;</code>\n\n"
            f"Contoh:\n"
            f"<code>/{message.command[0]} https://www.instagram.com/p/DcdCVwzkULZ/</code>"
        )

    link = message.command[1].strip()
    if not any(d in link for d in ("instagram.com", "instagr.am")):
        return await message.reply(
            "<b>❌</b> Link bukan dari Instagram. Harap berikan URL instagram.com."
        )

    status_msg = await message.reply(
        "<emoji id=5319190934510904031>⏳</emoji> <b>Processing Instagram post...</b>"
    )

    data = await _get_instagram_data(link)
    if not data.get("ok"):
        reason = data.get("reason", "unknown")
        if reason == "unavailable_or_private":
            err = (
                "<b>❌ Post tidak tersedia.</b>\n\n"
                "Kemungkinan post private / sudah dihapus.\n"
                "Untuk post private: taruh <code>cookies.txt</code> (format yt-dlp) "
                "di root project atau set <code>IG_COOKIES_FILE</code>, "
                "akun cookies harus follow akun post-nya."
            )
        elif reason == "rate_limited":
            err = "<b>❌ Rate limited oleh Instagram.</b> Coba lagi beberapa menit lagi."
        else:
            err = f"<b>❌ Gagal mengambil data Instagram.</b>\n<code>{reason}</code>"
        return await status_msg.edit(err)

    if not data.get("media"):
        return await status_msg.edit("<b>❌ Tidak ada media yang ditemukan.</b>")

    keyb = _url_keyboard(data)
    try:
        await status_msg.edit_rich(
            InputRichMessage(html=_build_rich_card(data)),
            reply_markup=keyb,
        )
    except Exception as e:
        LOGGER.warning("igdl edit rich gagal (%s): %s, fallback plain", e.__class__.__name__, e)
        try:
            await status_msg.edit(_build_plain_card(data), reply_markup=keyb)
        except Exception as e2:
            LOGGER.error("igdl edit plain gagal: %s", e2)


@app.on_message(filters.command(["twitterdl"], COMMAND_HANDLER))
@capture_err
async def twitterdl(_, message):
    if len(message.command) == 1:
        return await message.reply(
            f"Use command /{message.command[0]} [link] to download Twitter video."
        )
    url = message.command[1]
    if "x.com" in url:
        url = url.replace("x.com", "twitter.com")
    msg = await message.reply("<emoji id=5319190934510904031>⏳</emoji> Processing..")
    try:
        headers = {
            "Host": "ssstwitter.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "HX-Request": "true",
            "Origin": "https://ssstwitter.com",
            "Referer": "https://ssstwitter.com/id",
            "Cache-Control": "no-cache",
        }
        data = {
            "id": url,
            "locale": "id",
            "tt": "bc9841580b5d72e855e7d01bf3255278l",
            "ts": "1691416179",
            "source": "form",
        }
        post = await fetch.post(
            "https://ssstwitter.com/id",
            data=data,
            headers=headers,
            follow_redirects=True,
        )
        if post.status_code not in [200, 401]:
            return await msg.edit("Unknown error.")
        soup = BeautifulSoup(post.text, "lxml")
        cekdata = soup.find(
            "a",
            {
                "pure-button pure-button-primary is-center u-bl dl-button download_link without_watermark vignette_active"
            },
        )
        if not cekdata:
            return await message.reply(
                "ERROR: Oops! It seems that this tweet doesn't have a video! Try later or check your link"
            )
        try:
            fname = (
                (await fetch.head(cekdata.get("href")))
                .headers.get("content-disposition", "")
                .split("filename=")[1]
            )
            obj = SmartDL(cekdata.get("href"), progress_bar=False, timeout=15)
            obj.start()
            path = obj.get_dest()
            await message.reply_video(
                path,
                caption=f"<code>{fname}</code>\n\nUploaded for {message.from_user.mention} [<code>{message.from_user.id}</code>]",
            )
        except Exception as er:
            LOGGER.error("ERROR: while fetching TwitterDL. %s", er)
            return await msg.edit("ERROR: Got error while extracting link.")
        await msg.delete()
    except Exception as e:
        await message.reply(f"Failed to download twitter video..\n\n<b>Reason:</b> {e}")
        await msg.delete()


@app.on_message(filters.command(["tiktokdl", "ttdl"], COMMAND_HANDLER))
@capture_err
async def tiktokdl(_, message):
    if len(message.command) == 1:
        return await message.reply(
            "<b>🎵 TikTok Downloader</b>\n\n"
            f"Gunakan: <code>/{message.command[0]} &lt;link&gt;</code>\n\n"
            "Contoh:\n"
            f"<code>/{message.command[0]} https://vt.tiktok.com/ZSqDfLf8d/</code>"
        )

    link = message.command[1].strip()
    if not any(d in link for d in ("tiktok.com", "tiktokv.com", "vt.tiktok")):
        return await message.reply(
            "<b>❌</b> Link bukan dari TikTok. Harap berikan URL tiktok.com."
        )

    status_msg = await message.reply(
        "<emoji id=5319190934510904031>⏳</emoji> <b>Processing TikTok post...</b>"
    )

    data = await _get_tiktok_data(link)
    if not data.get("ok"):
        reason = data.get("reason", "unknown")
        if reason == "unavailable":
            err = (
                "<b>❌ Post tidak tersedia.</b>\n\n"
                "Kemungkinan post private / sudah dihapus."
            )
        elif reason == "rate_limited":
            err = "<b>❌ Rate limited.</b> Coba lagi beberapa detik lagi."
        else:
            detail = data.get("detail") or reason
            err = f"<b>❌ Gagal mengambil data TikTok.</b>\n<code>{_esc(str(detail)[:200])}</code>"
        return await status_msg.edit(err)

    if not data.get("media"):
        return await status_msg.edit("<b>❌ Tidak ada media yang ditemukan.</b>")

    keyb = _tt_keyboard(data)
    try:
        await status_msg.edit_rich(
            InputRichMessage(html=_tt_rich_card(data)),
            reply_markup=keyb,
        )
    except Exception as e:
        LOGGER.warning("tiktokdl edit rich gagal (%s): %s, fallback plain", e.__class__.__name__, e)
        try:
            await status_msg.edit(_tt_plain_card(data), reply_markup=keyb)
        except Exception as e2:
            LOGGER.error("tiktokdl edit plain gagal: %s", e2)


@app.on_message(filters.command(["fbdl", "fb"], COMMAND_HANDLER))
@capture_err
async def fbdl(_, message):
    if len(message.command) == 1:
        return await message.reply(
            f"Gunakan: <code>/{message.command[0]} &lt;link&gt;</code>\n\n"
            f"Contoh:\n<code>/{message.command[0]} https://www.facebook.com/share/p/18qRpLjJEk/</code>"
        )

    link = message.command[1].strip()
    if not any(d in link for d in ("facebook.com", "fb.watch", "fb.me")):
        return await message.reply("<b>❌</b> Link bukan dari Facebook.")

    status_msg = await message.reply(
        "<emoji id=5319190934510904031>⏳</emoji> <b>Processing Facebook post...</b>"
    )

    data = await _get_facebook_data(link)
    if not data.get("ok") or not data.get("media"):
        return await status_msg.edit(
            "<b>❌ Gagal mengambil data Facebook.</b>\n\n"
            "Kemungkinan: post private / grup tertutup / link butuh login.\n"
            f"<code>{data.get('reason', 'no_media')}</code>"
        )

    keyb = _fb_keyboard(data)
    try:
        await status_msg.edit_rich(InputRichMessage(html=_fb_rich_card(data)), reply_markup=keyb)
    except Exception as e:
        LOGGER.warning("fbdl rich gagal (%s): %s, fallback plain", e.__class__.__name__, e)
        try:
            await status_msg.edit(_fb_plain_card(data), reply_markup=keyb)
        except Exception as e2:
            LOGGER.error("fbdl plain gagal: %s", e2)
