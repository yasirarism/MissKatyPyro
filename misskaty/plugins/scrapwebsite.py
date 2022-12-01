# This plugin to scrape from melongmovie, and lk21
from bs4 import BeautifulSoup
import aiohttp
import re
import traceback
from misskaty import app
from pyrogram import filters
from pyrogram.errors import MessageTooLong
from misskaty.vars import COMMAND_HANDLER
from misskaty.core.decorator.errors import capture_err
from misskaty.helper.tools import rentry
from misskaty.helper.http import http

__MODULE__ = "WebScraper"
__HELP__ = """
/melongmovie - Scrape website data from MelongMovie Web. If without query will give latest movie list.
/lk21 [query <opsional>] - Scrape website data from LayarKaca21. If without query will give latest movie list.
/terbit21 [query <opsional>] - Scrape website data from Terbit21. If without query will give latest movie list.
/savefilm21 [query <opsional>] - Scrape website data from Savefilm21. If without query will give latest movie list.
/movieku [query <opsional>] - Scrape website data from Movieku.cc
/gomov [query <opsional>] - Scrape website data from GoMov. If without query will give latest movie list.
"""


# Broken
@app.on_message(filters.command(["nodrakor"], COMMAND_HANDLER))
@capture_err
async def nodrakor(_, message):
    try:
        judul = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        judul = ""

    msg = await message.reply("Sedang proses scrap, mohon tunggu..")
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        html = await http.get(f"https://109.234.34.246/?s={judul}", headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="content-thumbnail text-center")
        data = []
        for i in res:
            link = i.find_all("a")[0]["href"]
            judul = i.find_all("a")[0]["title"].split(": ")[1]
            data.append({"judul": judul, "link": link})
        if not data:
            return await msg.edit("Oops, data film tidak ditemukan.")
        res = "".join(f"<b>{i['judul']}</b>\n{i['link']}\n\n" for i in data)
        await msg.edit(
            f"<b>Hasil Pencarian di Nodrakor:</b>\n{res}\nScraped by @MissKatyRoBot"
        )
    except Exception as e:
        await msg.edit(f"ERROR: {str(e)}")


# Broken
@app.on_message(filters.command(["ngefilm21"], COMMAND_HANDLER))
@capture_err
async def ngefilm21(_, message):
    if len(message.command) == 1:
        return await message.reply("Masukkan query yang akan dicari..!!")
    title = message.text.split(" ", maxsplit=1)[1]

    msg = await message.reply("Sedang proses scrap, mohon tunggu..")
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(
            f"http://185.237.253.209/search?q={title}", headers=headers
        )
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all("h2")
        data = []
        for i in res:
            a = i.find_all("a")[0]
            judul = a.find_all(class_="r-snippetized")
            b = i.find_all("a")[0]["href"]
            data.append({"judul": judul[0].text, "link": b})
            # print(f"{judul[0].text}{b}\n")
        if not data:
            return await msg.edit("Oops, data film tidak ditemukan.")
        res = "".join(f"<b>{i['judul']}</b>\n{i['link']}\n" for i in data)
        await msg.edit(f"<b>Hasil Scrap dari Ngefilm21:</b>\n{res}")
    except Exception as e:
        await msg.edit(f"ERROR: {str(e)}")


# Scrape Web From Movieku.CC
@app.on_message(filters.command(["movieku"], COMMAND_HANDLER))
@capture_err
async def movikucc(_, message):
    if len(message.command) == 1:
        return await message.reply("Masukkan query yang akan dicari..!!")
    judul = message.text.split(" ", maxsplit=1)[1]
    msg = await message.reply("Sedang proses scrap, mohon tunggu..")
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        html = await http.get(f"https://107.152.39.187/?s={judul}", headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        data = soup.find_all(class_="bx")
        res = "".join(
            f"<b>Judul: {i.find_all('a')[0]['title']}</b>\nLink: {i.find_all('a')[0]['href']}\n\n"
            for i in data
        )
        await msg.edit(
            f"<b>Hasil Scrap di Movieku.cc:</b>\n{res} ⚠️ Gunakan command /movieku_scrap <b>[link]</b> untuk mengambil link download (hanya untuk movie)."
        )
    except Exception as e:
        await msg.edit(f"ERROR: {str(e)}")


@app.on_message(filters.command(["savefilm21"], COMMAND_HANDLER))
@capture_err
async def savefilm21(_, message):
    if len(message.command) == 1:
        return await message.reply("Masukkan query yang akan dicari..!!")
    judul = message.text.split(" ", maxsplit=1)[1]
    msg = await message.reply("Sedang proses scrap, mohon tunggu..")
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(
            f"http://38.242.196.210/?s={judul}", headers=headers, allow_redirects=False
        )
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="entry-title")
        data = []
        for i in res:
            pas = i.find_all("a")
            judul = pas[0].text
            link = pas[0]["href"]
            data.append({"judul": judul, "link": link})
        if not data:
            return await msg.edit("Oops, data film tidak ditemukan")
        res = "".join(
            f"<b>Judul: {i['judul']}</b>\nLink: {i['link']}\n\n" for i in data
        )
        await msg.edit(
            f"Hasil Scrap <code>{judul}</code> dari Savefilm21:\n{res}\n\n⚠️ Gunakan /savefilm21_scrap <b>[link]</b> untuk mengambil link downloadnya."
        )
    except Exception as e:
        await msg.edit(f"ERROR: {str(e)}")


@app.on_message(filters.command(["melongmovie"], COMMAND_HANDLER))
@capture_err
async def melongmovie(_, message):
    try:
        judul = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        judul = ""

    msg = await message.reply("Sedang proses scrap, mohon tunggu..")
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(f"http://167.99.31.48/?s={judul}", headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        data = []
        for res in soup.select(".box"):
            dd = res.select("a")
            url = dd[0]["href"]
            title = dd[0]["title"]
            try:
                kualitas = dd[0].find(class_="quality").text
            except:
                kualitas = ""
            data.append({"judul": title, "link": url, "kualitas": kualitas})
        if not data:
            return await msg.edit("Oops, data film tidak ditemukan di melongmovie")
        res = "".join(
            f"<b>Judul: {i['judul']}</b>\n<b>Kualitas:</b> {i['kualitas']}\n<b>Link</b>: {i['link']}\n\n"
            for i in data
        )
        # return await message.reply(json.dumps(data, indent=2, ensure_ascii=False))
        return await msg.edit(res)
    except Exception as e:
        await msg.edit(f"ERROR: {str(e)}")


@app.on_message(filters.command(["terbit21"], COMMAND_HANDLER))
@capture_err
async def terbit21_scrap(_, message):
    if len(message.command) == 1:
        r = await http.get("https://yasirapi.eu.org/terbit21")
        res = r.json()
        data = "".join(
            f"**Judul: {i['judul']}**\n`{i['kategori']}`\n{i['link']}\n**Download:** [Klik Disini]({i['dl']})\n\n"
            for i in res["result"]
        )
        try:
            return await message.reply(
                f"**Daftar rilis movie terbaru di web Terbit21**:\n{data}",
                disable_web_page_preview=True,
            )
        except MessageTooLong:
            msg = await rentry(data)
            return await message.reply(
                f"Karena hasil scrape terlalu panjang, maka hasil scrape di post ke rentry.\n\n{msg}"
            )
    judul = message.text.split(" ", maxsplit=1)[1]
    msg = await message.reply(f"Mencari film di Terbit21 dg keyword {judul}..")
    r = await http.get(f"https://yasirapi.eu.org/terbit21?q={judul}")
    res = r.json()
    data = "".join(
        f"**Judul: {i['judul']}**\n`{i['kategori']}`\n{i['link']}\n**Download:** [Klik Disini]({i['dl']})\n\n"
        for i in res["result"]
    )
    if not res["result"]:
        return await msg.edit("Yahh, ga ada hasil ditemukan")
    try:
        await msg.edit(
            f"<b>Hasil pencarian query {judul} di lk21:</b>\n{data}",
            disable_web_page_preview=True,
        )
    except MessageTooLong:
        pesan = await rentry(data)
        await msg.edit(
            f"Karena hasil scrape terlalu panjang, maka hasil scrape di post ke rentry.\n\n{pesan}"
        )


@app.on_message(filters.command(["lk21"], COMMAND_HANDLER))
@capture_err
async def lk21_scrap(_, message):
    if len(message.command) == 1:
        msg = await message.reply("Mendapatkan daftar post film terbaru di lk21")
        r = await http.get("https://yasirapi.eu.org/lk21")
        res = r.json()
        if res.get("detail", None):
            return await msg.edit(f"ERROR: {res['detail']}")
        data = "".join(
            f"**Judul: {i['judul']}**\n`{i['kategori']}`\n{i['link']}\n**Download:** [Klik Disini]({i['dl']})\n\n"
            for i in res["result"]
        )
        try:
            return await msg.edit(
                f"**Daftar rilis movie terbaru di web LK21**:\n{data}",
                disable_web_page_preview=True,
            )
        except MessageTooLong:
            msg = await rentry(data)
            await msg.edit(
                f"Karena hasil scrape terlalu panjang, maka hasil scrape di post ke rentry.\n\n{msg}"
            )
    judul = message.text.split(" ", maxsplit=1)[1]
    msg = await message.reply(f"Mencari film di lk21 dg keyword {judul}..")
    r = await http.get(f"https://yasirapi.eu.org/lk21?q={judul}")
    res = r.json()
    if res.get("detail", None):
        return await msg.edit(f"ERROR: {res['detail']}")
    data = "".join(
        f"**Judul: {i['judul']}**\n`{i['kategori']}`\n{i['link']}\n**Download:** [Klik Disini]({i['dl']})\n\n"
        for i in res["result"]
    )
    if not res["result"]:
        return await msg.edit("Yahh, ga ada hasil ditemukan")
    try:
        await msg.edit(
            f"<b>Hasil pencarian query {judul} di lk21:</b>\n{data}",
            disable_web_page_preview=True,
        )
    except MessageTooLong:
        pesan = await rentry(data)
        return await msg.edit(
            f"Karena hasil scrape terlalu panjang, maka hasil scrape di post ke rentry.\n\n{pesan}"
        )


@app.on_message(filters.command(["gomov", "gomov@MissKatyRoBot"], COMMAND_HANDLER))
@capture_err
async def gomov_scrap(_, message):
    try:
        judul = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        judul = ""

    msg = await message.reply("Scraping GoMov Website..")
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(f"https://185.173.38.216/?s={judul}", headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        entry = soup.find_all(class_="entry-title")
        DATA = []
        for i in entry:
            judul = i.find_all("a")[0].text
            link = i.find_all("a")[0]["href"]
            DATA.append({"judul": judul, "link": link})
        if not DATA:
            return await msg.edit("Oops, data film tidak ditemukan di GoMov")
        res = "".join(f"<b>Judul: {i['judul']}</b>\n{i['link']}\n\n" for i in DATA)
        await msg.edit(
            f"<b>Hasil Pencarian di website GoMov:</b>\n{res}\nScraped by @MissKatyRoBot"
        )
    except Exception:
        exc = traceback.format_exc()
        await msg.edit(f"ERROR: <code>{exc}</code>")


@app.on_message(
    filters.command(
        ["savefilm21_scrap", "savefilm21_scrap@MissKatyRoBot"], COMMAND_HANDLER
    )
)
@capture_err
async def savefilm21_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(link, headers=headers, follow_redirects=False)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="button button-shadow")
        res = "".join(f"{i.text}\n{i['href']}\n\n" for i in res)
        await message.reply(f"<b>Hasil Scrap dari {link}</b>:\n\n{res}")
    except IndexError:
        return await message.reply(
            "Gunakan command /savefilm21_scrap <b>[link]</b> untuk scrap link download"
        )
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


@app.on_message(
    filters.command(["nodrakor_scrap", "nodrakor_scrap@MissKatyRoBot"], COMMAND_HANDLER)
)
@capture_err
async def nodrakor_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(link, headers=headers, follow_redirects=False)
        soup = BeautifulSoup(html.text, "lxml")
        hasil = soup.find_all(class_="gmr-download-wrap clearfix")[0]
        await message.reply(f"<b>Hasil Scrap dari {link}</b>:\n{hasil}")
    except IndexError:
        return await message.reply(
            "Gunakan command /nodrakor_scrap <b>[link]</b> untuk scrap link download"
        )
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


# Scrape Link Download Movieku.CC
@app.on_message(
    filters.command(["movieku_scrap", "movieku_scrap@MissKatyRoBot"], COMMAND_HANDLER)
)
@capture_err
async def muviku_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        res = soup.find_all(class_="smokeurl")
        data = []
        for i in res:
            for b in range(len(i.find_all("a"))):
                link = i.find_all("a")[b]["href"]
                kualitas = i.find_all("a")[b].text
                # print(f"{kualitas}\n{link
                data.append({"link": link, "kualitas": kualitas})
        if not data:
            return await message.reply("Oops, data film tidak ditemukan.")
        res = "".join(f"<b>Host: {i['kualitas']}</b>\n{i['link']}\n\n" for i in data)
        await message.reply(res)
    except IndexError:
        return await message.reply(
            "Gunakan command /movieku_scrap <b>[link]</b> untuk scrap link download"
        )
    except Exception as e:
        await message.reply(f"ERROR: {str(e)}")


@app.on_message(
    filters.command(["melong", "melong@MissKatyRoBot"], COMMAND_HANDLER)
    & filters.user([617426792, 1985689491, 1172699512, 2024984460])
)
@capture_err
async def melong_scrap(_, message):
    try:
        link = message.text.split(" ", maxsplit=1)[1]
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = await http.get(link, headers=headers)
        soup = BeautifulSoup(html.text, "lxml")
        for ep in soup.findAll(text=re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
            hardsub = ep.findPrevious("div")
            softsub = ep.findNext("div")
            rep = f"{hardsub}\n{softsub}"
            await message.reply(rep)
    except IndexError:
        await message.reply(
            "Gunakan command /melong <b>[link]</b> untuk scrap link download"
        )
