from bot import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import COMMAND_HANDLER
from bot.core.decorator.errors import capture_err
from bot.plugins.dev import shell_exec
import json, os, base64
from time import perf_counter
from re import split as ngesplit, I
from bot.helper.tools import get_random_string

ARCH_EXT = [
    ".mkv",
    ".avi",
    ".mp4",
    ".mov"
]

def get_base_name(orig_path: str):
    if ext := [ext for ext in ARCH_EXT if orig_path.lower().endswith(ext)]:
        ext = ext[0]
        return ngesplit(f"{ext}$", orig_path, maxsplit=1, flags=I)[0]

def get_subname(url, format):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if format == "ass":
        frmt = "ass"
    else:
        frmt = "srt"
    if scheme_removed.find("/") == -1:
        return f"MissKatySub_{get_random_string(4)}.{frmt}"
    return get_base_name(os.path.basename(scheme_removed)) + f".{frmt}"

DATA = {}

@app.on_message(filters.command(["ceksub"], COMMAND_HANDLER))
@capture_err
async def ceksub(_, m):
        cmd = m.text.split(" ", 1)
        if len(cmd) == 1:
            return await m.reply(f"Gunakan command /{m.command[0]} [link] untuk mengecek subtitle dan audio didalam video.")
        link = cmd[1]
        start_time = perf_counter()
        pesan = await m.reply("Sedang memproses perintah..", quote=True)
        res = (await shell_exec(f"ffprobe -loglevel 0 -print_format json -show_format -show_streams {link}"))[0]
        details = json.loads(res)
        buttons = []
        DATA[f"{m.chat.id}-{msg.message_id}"] = {}
        for stream in details["streams"]:
            mapping = stream["index"]
            try:
                stream_name = stream["codec_name"]
            except:
                stream_name = "-"
            stream_type = stream["codec_type"]
            if stream_type in ("audio", "subtitle"):
                pass
            else:
                continue
            try:
                lang = stream["tags"]["language"]
            except:
                lang = mapping
            DATA.append({"mapping": mapping, "stream_name": stream_name, "stream_type": stream_type, "lang": lang})
            buttons.append([
                InlineKeyboardButton(
                    f"0:{mapping}({lang}): {stream_type}: {stream_name}", f"streamextract_{stream_type}_{mapping}_{m.chat.id}_{m.message_id}"
                )
            ])
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        btn = [
            [
                InlineKeyboardButton(
                    text=f"0:{data.get('mapping')}({data.get('lang')}): {data.get('stream_type')}: {data.get('stream_name')}",
                    callback_data=f"streamextract_0:{data.get('mapping')}_{data.get('stream_name')}",
                )
            ]
            for data in DATA
        ]
        buttons.append([
            InlineKeyboardButton("Cancel","cancel")
        ])
        await pesan.edit(f"Gunakan command /extractsub <b>[link] [index -> angka setelah 0:]</b> untuk extract subtitle (Ex: /extractsub [LINK] 2 -> untuk extract sub index ke dua, dan command /converttosrt untuk convert ass ke srt. Hanya support direct link & format (.ass, .srt) saja saat ini.\nProcessed in {timelog}", reply_markup=InlineKeyboardMarkup(buttons))


ALLOWED_USER = [978550890, 617426792, 2024984460, 1533008300, 1985689491]


@app.on_message(filters.command(["converttosrt"], COMMAND_HANDLER))
@capture_err
async def convertsrt(_, m):
    reply = m.reply_to_message
    if not reply and reply.document:
        return await m.reply(f"Gunakan command /{m.command[0]} dengan mereply ke file ass untuk convert subtitle ke srt.")
    msg = await m.reply("Sedang memproses perintah...")
    dl = await reply.download()
    (await shell_exec(f"ffmpeg -i {dl} {os.path.basename(dl)}.srt"))[0]
    await m.reply_document(f"{os.path.basename(dl)}.srt", caption=f"{os.path.basename(dl)}.srt")
    await msg.delete()
    try:
        os.remove(dl)
        os.remove(f"{os.path.basename(dl)}.srt")
    except:
        pass

    
@app.on_message(filters.regex("^streamextract_"))
async def streamextract(bot, update):
    cb_data = update.data
    usr = update.message.reply_to_message
    if update.from_user.id != usr.from_user.id:
        return await quer_y.answer("⚠️ Akses Denied!", True)
    _, mapping, type = cb_data.split("_")

@app.on_message(filters.command(["extractsub"], COMMAND_HANDLER))
@capture_err
async def extractsub(_, m):
    cmd = m.text.split(" ", 1)
    if len(cmd) == 1:
        return await m.reply(f"Gunakan command /{m.command[0]} <b>[link] [index]</b> untuk ekstrak subtitle dalam video.")
    msg = await m.reply("Sedang memproses perintah...")
    try:
        link = m.command[1]
        index = m.command[2]
        start_time = perf_counter()
        getformat_cmd = (await shell_exec(f"ffprobe -loglevel 0 -print_format json -show_streams {link}"))[0]
        format = json.loads(getformat_cmd)
        namafile = get_subname(link, format["streams"][int(index)]["codec_name"])
        extract = (await shell_exec(f"ffmpeg -i {link} -map 0:{index} {namafile}"))[0]
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        await m.reply_document(namafile, caption=f"<b>Nama File:</b> <code>{namafile}</code>\n\nDiekstrak oleh @MissKatyRoBot dalam waktu {timelog}")
        await msg.delete()
        try:
            os.remove(namafile)
        except:
            pass
    except IndexError:
        await msg.edit(f"Gunakan command /{m.command[0]} <b>[link] [index]</b> untuk extract subtitle dalam video")
    except Exception as e:
        await msg.edit(f"Gagal ekstrak sub, pastikan kamu menggunakan perasaan kamu saat menggunakan command ini..\n\nERROR: {e}")
