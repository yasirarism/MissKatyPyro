from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER
from bot.utils.decorator import capture_err
from bot.plugins.dev import shell_exec
import json, os
from time import perf_counter
from bot.utils.tools import get_random_string
from os import path

def get_subname(url):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return f'MissKatySub_{get_random_string(4)}.srt'
    return path.basename(scheme_removed)

@app.on_message(filters.command(["ceksub"], COMMAND_HANDLER))
@capture_err
async def ceksub(_, m):
    cmd = m.text.split(' ', 1)
    if len(cmd) == 1:
        return await m.reply(
            f'Gunakan command /{m.command[0]} [link] untuk mengecek subtitle dan audio didalam video.'
        )
    link = cmd[1]
    if link.startswith("https://file.yasirweb.my.id"):
        link = link.replace("https://file.yasirweb.my.id", "https://file.yasiraris.workers.dev")
    start_time = perf_counter()
    pesan = await m.reply("Sedang memproses perintah..")
    try:
        res = (await shell_exec(
            f"ffprobe -loglevel 0 -print_format json -show_format -show_streams {link}"
        ))[0]
        details = json.loads(res)
        DATA = []
        for stream in details["streams"]:
            mapping = stream['index']
            try:
                stream_name = stream['codec_name']
            except:
                stream_name = "-"
            stream_type = stream['codec_type']
            if stream_type in ("audio", "subtitle"):
                pass
            else:
                continue
            try:
                lang = stream["tags"]["language"]
            except:
                lang = mapping
            DATA.append({
                'mapping': mapping,
                'stream_name': stream_name,
                'stream_type': stream_type,
                'lang': lang
            })
        res = "".join(
            f"<b>Index:</b> {i['mapping']}\n<b>Stream Name:</b> {i['stream_name']}\n<b>Language:</b> {i['lang']}\n\n"
            for i in DATA)
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        await pesan.edit(
            f"<b>Daftar Sub & Audio File:</b>\n{res}\nGunakan command /extractsub <b>[link] [index]</b> untuk extract subtitle. Hanya support direct link & format .srt saja saat ini.\nProcessed in {timelog}"
        )
    except Exception as e:
        await pesan.edit(
            f"Gagal ekstrak sub, pastikan kamu menggunakan perasaan kamu saat menggunakan command ini..\n\nERROR: {e}"
        )


ALLOWED_USER = [978550890, 617426792, 2024984460]


@app.on_message(filters.command(["extractsub"], COMMAND_HANDLER))
@capture_err
async def extractsub(_, m):
    cmd = m.text.split(' ', 1)
    if len(cmd) == 1:
        return await m.reply(
            f'Gunakan command /{m.command[0]} <b>[link] [index]</b> untuk ekstrak subtitle dalam video.'
        )
    msg = await m.reply("Sedang memproses perintah...")
    try:
        link = m.command[1]
        if link.startswith("https://file.yasirweb.my.id"):
            link = link.replace("https://file.yasirweb.my.id", "https://file.yasiraris.workers.dev")
        index = m.command[2]
        if m.from_user.id not in ALLOWED_USER:
            return msg.edit(
                "Hehehe, silahkan donasi jika ingin menggunakan fitur ini :)")
        start_time = perf_counter()
        namafile = get_subname(link)
        extract = (
            await shell_exec(f"ffmpeg -i {link} -map 0:{index} {namafile}"))[0]
        end_time = perf_counter()
        timelog = "{:.2f}".format(end_time - start_time) + " second"
        await m.reply_document(
            namafile,
            caption=
            f"<b>Nama File:</b> <code>{namafile}</code>\n\nDiekstrak oleh @MissKatyRoBot dalam waktu {timelog}"
        )
        await msg.delete()
        try:
            os.remove(namafile)
        except:
            pass
    except IndexError:
        await msg.edit(
            f"Gunakan command /{m.command[0]} <b>[link] [index]</b> untuk extract subtitle dalam video"
        )
    except Exception as e:
        await msg.edit(
            f"Gagal ekstrak sub, pastikan kamu menggunakan perasaan kamu saat menggunakan command ini..\n\nERROR: {e}"
        )
