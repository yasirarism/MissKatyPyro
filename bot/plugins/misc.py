import os
import aiohttp
from bs4 import BeautifulSoup
import json
import requests
from pyrogram import Client, filters
from gpytranslate import Translator
from requests.utils import requote_uri
from gtts import gTTS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from info import IMDB_TEMPLATE, COMMAND_HANDLER
from utils import extract_user, get_file_id, get_poster, last_online
from bot.utils.time_gap import check_time_gap
import time
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command(['google','google@MissKatyRoBot'], COMMAND_HANDLER))
async def gsearch(client, message):
    if len(message.command) == 1:
        await message.reply("Give a query to search!")
        return
    query = message.text.split(" ", maxsplit=1)[1]
    msg = await message.reply_text(f"**Googling** for `{query}` ...")
    try:
       headers = {
         'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
       }
       html = requests.get(f'https://www.google.com/search?q={query}', headers=headers)
       soup = BeautifulSoup(html.text, 'lxml')

       # collect data
       data = []

       for result in soup.select('.tF2Cxc'):
          title = result.select_one('.DKV0Md').text
          link = result.select_one('.yuRUbf a')['href']
          try:
            snippet = result.select_one('#rso .lyLwlc').text
          except:
            snippet = "-"

          # appending data to an array
          data.append({
            'title': title,
            'link': link,
            'snippet': snippet,
          })
       arr = json.dumps(data, indent=2, ensure_ascii=False)
       parse = json.loads(arr)
       total = len(parse)
       res = "".join(f"<a href='{i['link']}'>{i['title']}</a>\n{i['snippet']}\n\n" for i in parse)
    except Exception as e:
       await msg.edit(e)
       return
    await msg.edit(text=f"<b>Ada {total} Hasil Pencarian dari {query}:</b>\n{res}<b>Scraped by @MissKatyRoBot</b>", disable_web_page_preview=True)

@Client.on_message(filters.command(["tr","trans","translate","tr@MissKatyRoBot","trans@MissKatyRoBot","translate@MissKatyRoBot"], COMMAND_HANDLER))
async def translate(client, message):
    trl = Translator()
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        if len(message.text.split()) == 1:
            target_lang = "id"
        else:
            target_lang = message.text.split()[1]
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            text = message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            await message.reply_text(
                "Berikan Kode bahasa yang valid.\n[Available options](https://telegra.ph/Lang-Codes-11-08).\n<b>Usage:</b> <code>/tr en</code>",
            )
            return
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    msg = await message.reply("Menerjemahkan...")
    detectlang = await trl.detect(text)
    try:
        tekstr = await trl(text, targetlang=target_lang)
    except ValueError as err:
        await msg.edit(f"Error: <code>{str(err)}</code>")
        return
    return await msg.edit(
        f"<b>Diterjemahkan:</b> dari {detectlang} ke {target_lang} \n<code>``{tekstr.text}``</code>",
    )

@Client.on_message(filters.command(["tts","tts@MissKatyRoBot"], COMMAND_HANDLER))
async def tts(_, message):
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        if len(message.text.split()) == 1:
            target_lang = "id"
        else:
            target_lang = message.text.split()[1]
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            text = message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            await message.reply_text(
                "Berikan Kode bahasa yang valid.\n[Available options](https://telegra.ph/Lang-Codes-11-08).\n<b>Usage:</b> <code>/trt en <text></code>",
            )
            return
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    msg = await message.reply("Converting to voice...")
    try:
        tts = gTTS(text, lang=target_lang)
        tts.save(f'tts_{message.from_user.id}.mp3')
    except ValueError as err:
        await msg.edit(f"Error: <code>{str(err)}</code>")
        return
    await msg.delete()
    return await msg.reply_audio(f'tts_{message.from_user.id}.mp3')

@Client.on_message(filters.command(["tosticker","tosticker@MissKatyRoBot"], COMMAND_HANDLER))
async def tostick(client, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply_text("Reply ke foto untuk mengubah ke sticker")
        sticker = await client.download_media(message.reply_to_message.photo.file_id, f"tostick_{message.from_user.id}.webp")
        await message.reply_sticker(sticker)
        os.remove(sticker)
    except Exception as e:
        await message.reply_text(str(e))

@Client.on_message(filters.command(["toimage","toimage@MissKatyRoBot"], COMMAND_HANDLER))
async def topho(client, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.sticker:
            return await message.reply_text("Reply ke sticker untuk mengubah ke foto")
        if message.reply_to_message.sticker.is_animated:
            return await message.reply_text("Ini sticker animasi, command ini hanya untuk sticker biasa.")
        photo = await client.download_media(message.reply_to_message.sticker.file_id, f"tostick_{message.from_user.id}.jpg")
        await message.reply_photo(photo=photo, caption=f'Sticker -> Image\n@MissKatyRoBot')
        os.remove(photo)
    except Exception as e:
        await message.reply_text(str(e))

@Client.on_message(filters.command(['id','id@MissKatyRoBot'], COMMAND_HANDLER))
async def showid(client, message):
    chat_type = message.chat.type
    if chat_type == "private":
        user_id = message.chat.id
        first = message.from_user.first_name
        last = message.from_user.last_name or ""
        username = message.from_user.username
        dc_id = message.from_user.dc_id or ""
        await message.reply_text(
            f"<b>➲ First Name:</b> {first}\n<b>➲ Last Name:</b> {last}\n<b>➲ Username:</b> {username}\n<b>➲ Telegram ID:</b> <code>{user_id}</code>\n<b>➲ Data Centre:</b> <code>{dc_id}</code>",
            quote=True
        )

    elif chat_type in ["group", "supergroup"]:
        _id = ""
        _id += (
            "<b>➲ Chat ID</b>: "
            f"<code>{message.chat.id}</code>\n"
        )
        if message.reply_to_message:
            _id += (
                "<b>➲ User ID</b>: "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
                "<b>➲ Replied User ID</b>: "
                f"<code>{message.reply_to_message.from_user.id if message.reply_to_message.from_user else 'Anonymous'}</code>\n"
            )
            file_info = get_file_id(message.reply_to_message)
        else:
            _id += (
                "<b>➲ User ID</b>: "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
            )
            file_info = get_file_id(message)
        if file_info:
            _id += (
                f"<b>{file_info.message_type}</b>: "
                f"<code>{file_info.file_id}</code>\n"
            )
        await message.reply_text(
            _id,
            quote=True
        )

@Client.on_message(filters.command(["info","info@MissKatyRoBot"], COMMAND_HANDLER))
async def who_is(client, message):
    # https://github.com/SpEcHiDe/PyroGramBot/blob/master/pyrobot/plugins/admemes/whois.py#L19
    status_message = await message.reply_text(
        "`Fetching user info...`"
    )
    await status_message.edit(
        "`Processing user info...`"
    )
    from_user = None
    from_user_id, _ = extract_user(message)
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(str(error))
        return
    if from_user is None:
        return await status_message.edit("no valid user_id / message specified")
    message_out_str = ""
    message_out_str += f"<b>➲First Name:</b> {from_user.first_name}\n"
    last_name = from_user.last_name or "<b>None</b>"
    message_out_str += f"<b>➲Last Name:</b> {last_name}\n"
    message_out_str += f"<b>➲Telegram ID:</b> <code>{from_user.id}</code>\n"
    username = from_user.username or "<b>None</b>"
    dc_id = from_user.dc_id or "[User Doesnt Have A Valid DP]"
    message_out_str += f"<b>➲Data Centre:</b> <code>{dc_id}</code>\n"
    message_out_str += f"<b>➲User Name:</b> @{username}\n"
    message_out_str += f"<b>➲User 𝖫𝗂𝗇𝗄:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"
    if message.chat.type in (("supergroup", "channel")):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = datetime.fromtimestamp(
                chat_member_p.joined_date or time.time()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += (
                "<b>➲Joined this Chat on:</b> <code>"
                f"{joined_date}"
                "</code>\n"
            )
        except UserNotParticipant:
            pass
    chat_photo = from_user.photo
    if chat_photo:
        local_user_photo = await client.download_media(
            message=chat_photo.big_file_id
        )
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=reply_markup,
            caption=message_out_str,
            parse_mode="html",
            disable_notification=True
        )
        os.remove(local_user_photo)
    else:
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            quote=True,
            parse_mode="html",
            disable_notification=True
        )
    await status_message.delete()

async def get_content(url):
    async with aiohttp.ClientSession() as session:
        r = await session.get(url)
        return await r.read()

async def transapi(text):
    a = requests.get(f"https://script.google.com/macros/s/AKfycbyhNk6uVgrtJLEFRUT6y5B2pxETQugCZ9pKvu01-bE1gKkDRsw/exec?q={text}&target=id").json()
    return a['text']

# IMDB Versi Indonesia v1
@Client.on_message(filters.command(["imdb","imdb@MissKatyRoBot"], COMMAND_HANDLER))
async def imdb1_search(client, message):
    is_in_gap, sleep_time = await check_time_gap(message.from_user.id)
    if is_in_gap and message.from_user.id != 617426792:
        return await message.reply(f"Maaf, Silahkan tunggu <code>{str(sleep_time)} detik</code> sebelum menggunakan command ini lagi.")
    if ' ' in message.text:
        r, title = message.text.split(None, 1)
        k = await message.reply('Sedang mencari di Database IMDB.. 😴')
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await k.edit("Tidak ada hasil ditemukan.. 😕")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} ({movie.get('year')})",
                    callback_data=f"imdb1_{message.from_user.id}_{message.message_id}_{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('Silahkan klik tombol dibawah ini.. 👇', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Berikan aku nama series atau movie yang ingin dicari. 🤷🏻‍♂️')

@Client.on_callback_query(filters.regex('^imdb1'))
async def imdb1_callback(bot: Client, query: CallbackQuery):
    i, user, msg_id, movie = query.data.split('_')
    if user == f"{query.from_user.id}":
      await query.message.edit_text("Permintaan kamu sedang diproses.. ")
      try:
        trl = Translator()
        imdb = await get_poster(query=movie, id=True)
        resp = await get_content(f"https://www.imdb.com/title/tt{movie}/")
        req = requests.get(f"https://betterimdbot.herokuapp.com/?tt=tt{movie}")
        parse = req.json()
        b = BeautifulSoup(resp, "lxml")
        r_json = json.loads(b.find("script", attrs={"type": "application/ld+json"}).contents[0])
        res_str = ""
        if r_json["@type"] == 'Person':
            return query.answer("⚠ Tidak ada hasil ditemukan. Silahkan coba cari manual di Google..", show_alert=True)
        if parse.get("title"):
            res_str += f"<b>📹 Judul:</b> <a href='https://www.imdb.com/title/tt{movie}/'>{parse['title']}</a>"
        if parse.get("title_type"):
            res_str += f" ({parse['title_type']})\n"
        else:
            res_str += "\n"
        if imdb.get("kind") == "tv series":
            res_str += f"<b>🍂 Total Season:</b> <code>{imdb['seasons']} season</code>\n"
        if imdb.get("aka"):
            res_str += f"<b>🎤 AKA:</b> <code>{imdb['aka'].split(',')[0]}</code>\n\n"
        else:
            res_str += "\n"
        if parse.get("duration"):
            durasi = await trl(parse['duration'], targetlang='id')
            res_str += f"<b>🕓 Durasi:</b> <code>{durasi.text}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>🔞 Content Rating :</b> <code>{r_json['contentRating']}</code> \n"
        if parse.get("UserRating"):
            user_rating = await trl(parse['UserRating']['description'], targetlang='id')
            res_str += f"<b>⭐ Rating :</b> <code>{user_rating.text}</code>\n"
        if parse.get("release_date"):
            rilis = await trl(parse['release_date']['NAME'], targetlang='id')
            res_str += f"<b>📆 Tanggal Rilis :</b> <code>{rilis.text}</code>\n"
        if parse.get("genres"):
            all_genre = parse['genres']
            genre = "".join(f"{i} " for i in all_genre)
            res_str += f"<b>🔮 Genre :</b> {genre}\n"
        if imdb.get("countries"):
            all_country = imdb['countries']
            if all_country.endswith(", "):
               all_country = all_country[:-2]
            res_str += f"<b>🆔 Negara:</b> <code>{all_country}</code>\n"
        if imdb.get("languages"):
            all_lang = imdb['languages']
            if all_lang.endswith(", "):
               all_lang = all_lang[:-2]
            res_str += f"<b>🔊 Bahasa:</b> <code>{all_lang}</code>\n"
        if parse.get("sum_mary"):
            res_str += "\n<b>🙎 Info Pemeran:</b>\n"
            try:
                director = parse['sum_mary']['Directors']
                director_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in director)
                director_ = director_[:-2]
                res_str += f"<b>Sutradara:</b> {director_}\n"
            except:
                res_str += ""
            try:
                writers = parse['sum_mary']['Writers']
                writers_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in writers)
                writers_ = writers_[:-2]
                res_str += f"<b>Penulis:</b> {writers_}\n"
            except:
                res_str += ""
            try:
                stars = parse['sum_mary']['Stars']
                stars_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in stars)
                stars_ = stars_[:-2]
                res_str += f"<b>Bintang:</b> {stars_}\n"
            except:
                res_str += ""
            res_str += "\n"
        if r_json.get("trailer"):
            trailer_url = "https://imdb.com" + r_json['trailer']['embedUrl']
            markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com/title/tt{movie}/"),
                     InlineKeyboardButton("▶️ Trailer", url=trailer_url)
                    ]
                ])
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com/title/tt{movie}/")]])
        if imdb.get("plot"):
            try:
              summary = await trl(imdb['plot'], targetlang='id')
              res_str += f"<b>📜 Plot: </b> <code>{summary.text}</code>\n\n"
            except Exception:
              res_str += f"<b> 📜 Plot: -</b>\n"
        if r_json.get("keywords"):
            keywords = r_json['keywords'].split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Keyword/Tags:</b> {key_}\n"
        if parse.get("awards"):
            all_award = parse['awards']
            awards = await trl("".join(f"× {i}\n" for i in all_award), targetlang='id')
            res_str += f"<b>🏆 Penghargaan :</b>\n<code> {awards.text}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"IMDb Plugin by @MissKatyRoBot"
        thumb = parse.get('poster')
        if thumb:
            try:
                await query.message.reply_photo(photo=thumb, quote=True, caption=res_str, reply_to_message_id=int(msg_id), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace('.jpg', "._V1_UX360.jpg")
                await query.message.reply_photo(photo=poster, caption=res_str, reply_to_message_id=int(msg_id), reply_markup=markup)
            except Exception as e:
                logger.exception(e)
                await query.message.reply(res_str, reply_markup=markup, disable_web_page_preview=False, reply_to_message_id=int(msg_id))
            await query.message.delete()
        else:
            await query.message.edit(res_str, reply_markup=markup, disable_web_page_preview=False)
        await query.answer()
      except Exception as e:
        await query.message.edit_text(f"<b>ERROR:</b>\n<code>{e}</code>")
    else:
        await query.answer("Tombol ini bukan untukmu", show_alert=True)

# IMDB Versi Indonesia v2
@Client.on_message(filters.command(["imdb2","imdb2@MissKatyRoBot"], COMMAND_HANDLER))
async def imdb2_search(client, message):
    is_in_gap, sleep_time = await check_time_gap(message.from_user.id)
    if is_in_gap and message.from_user.id != 617426792:
        return await message.reply(f"Maaf, Silahkan tunggu <code>{str(sleep_time)} detik</code> sebelum menggunakan command ini lagi.")
    if ' ' in message.text:
        r, title = message.text.split(None, 1)
        k = await message.reply('Sedang mencari di Database IMDB.. 😴')
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await k.edit("Tidak ada hasil ditemukan.. 😕")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} ({movie.get('year')})",
                    callback_data=f"imdb2_{message.from_user.id}_{message.message_id}_{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('Silahkan klik tombol dibawah ini.. 👇', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Berikan aku nama series atau movie yang ingin dicari. 🤷🏻‍♂️')

@Client.on_callback_query(filters.regex('^imdb2'))
async def imdb2_callback(bot: Client, query: CallbackQuery):
    i, user, msg_id, movie = query.data.split('_')
    if user == f"{query.from_user.id}":
      await query.message.edit_text("Permintaan kamu sedang diproses.. ")
      try:
        trl = Translator()
        imdb = await get_poster(query=movie, id=True)
        resp = await get_content(f"https://www.imdb.com/title/tt{movie}/")
        req = requests.get(f"https://betterimdbot.herokuapp.com/?tt=tt{movie}")
        parse = req.json()
        b = BeautifulSoup(resp, "lxml")
        r_json = json.loads(b.find("script", attrs={"type": "application/ld+json"}).contents[0])
        res_str = ""
        if r_json["@type"] == 'Person':
            return query.answer("⚠ Tidak ada hasil ditemukan. Silahkan coba cari manual di Google..", show_alert=True)
        if parse.get("title"):
            res_str += f"<b>📹 Judul:</b> <a href='https://www.imdb.com/title/tt{movie}/'>{parse['title']}</a>"
        if parse.get("title_type"):
            res_str += f" ({parse['title_type']})\n"
        else:
            res_str += "\n"
        if imdb.get("kind") == "tv series":
            res_str += f"<b>🍂 Total Season:</b> <code>{imdb['seasons']} season</code>\n"
        if imdb.get("aka"):
            res_str += f"<b>🎤 AKA:</b> <code>{imdb['aka'].split(',')[0]}</code>\n\n"
        else:
            res_str += "\n"
        if parse.get("duration"):
            durasi = await transapi(parse['duration'])
            res_str += f"<b>🕓 Durasi:</b> <code>{durasi}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>🔞 Content Rating :</b> <code>{r_json['contentRating']}</code> \n"
        if parse.get("UserRating"):
            user_rating = await transapi(parse['UserRating']['description'])
            res_str += f"<b>⭐ Rating :</b> <code>{user_rating}</code>\n"
        if parse.get("release_date"):
            rilis = await transapi(parse['release_date']['NAME'])
            res_str += f"<b>📆 Tanggal Rilis :</b> <code>{rilis}</code>\n"
        if parse.get("genres"):
            all_genre = parse['genres']
            genre = "".join(f"{i} " for i in all_genre)
            res_str += f"<b>🔮 Genre :</b> {genre}\n"
        if imdb.get("countries"):
            all_country = imdb['countries']
            if all_country.endswith(", "):
               all_country = all_country[:-2]
            res_str += f"<b>🆔 Negara:</b> <code>{all_country}</code>\n"
        if imdb.get("languages"):
            all_lang = imdb['languages']
            if all_lang.endswith(", "):
               all_lang = all_lang[:-2]
            res_str += f"<b>🔊 Bahasa:</b> <code>{all_lang}</code>\n"
        if parse.get("sum_mary"):
            res_str += "\n<b>🙎 Info Pemeran:</b>\n"
            try:
                director = parse['sum_mary']['Directors']
                director_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in director)
                director_ = director_[:-2]
                res_str += f"<b>Sutradara:</b> {director_}\n"
            except:
                res_str += ""
            try:
                writers = parse['sum_mary']['Writers']
                writers_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in writers)
                writers_ = writers_[:-2]
                res_str += f"<b>Penulis:</b> {writers_}\n"
            except:
                res_str += ""
            try:
                stars = parse['sum_mary']['Stars']
                stars_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in stars)
                stars_ = stars_[:-2]
                res_str += f"<b>Bintang:</b> {stars_}\n"
            except:
                res_str += ""
            res_str += "\n"
        if r_json.get("trailer"):
            trailer_url = "https://imdb.com" + r_json['trailer']['embedUrl']
            markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com/title/tt{movie}/"),
                     InlineKeyboardButton("▶️ Trailer", url=trailer_url)
                    ]
                ])
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com/title/tt{movie}/")]])
        if imdb.get("plot"):
            try:
              summary = await transapi(imdb['plot'])
              res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
            except Exception:
              res_str += f"<b> 📜 Plot: -</b>\n"
        if r_json.get("keywords"):
            keywords = r_json['keywords'].split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Keyword/Tags:</b> {key_}\n"
        if parse.get("awards"):
            all_award = parse['awards']
            awards = await transapi("".join(f"× {i}\n" for i in all_award))
            res_str += f"<b>🏆 Penghargaan :</b>\n<code> {awards}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"IMDb Plugin by @MissKatyRoBot"
        thumb = parse.get('poster')
        if thumb:
            try:
                await query.message.reply_photo(photo=thumb, quote=True, caption=res_str, reply_to_message_id=int(msg_id), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace('.jpg', "._V1_UX360.jpg")
                await query.message.reply_photo(photo=poster, caption=res_str, reply_to_message_id=int(msg_id), reply_markup=markup)
            except Exception as e:
                logger.exception(e)
                await query.message.reply(res_str, reply_markup=markup, disable_web_page_preview=False, reply_to_message_id=int(msg_id))
            await query.message.delete()
        else:
            await query.message.edit(res_str, reply_markup=markup, disable_web_page_preview=False)
        await query.answer()
      except Exception as e:
        await query.message.edit_text(f"<b>ERROR:</b>\n<code>{e}</code>")
    else:
        await query.answer("Tombol ini bukan untukmu", show_alert=True)

# IMDB Versi English
@Client.on_message(filters.command(["imdb_en","imdb_en@MissKatyRoBot"], COMMAND_HANDLER))
async def imdb_en_search(client, message):
    if ' ' in message.text:
        r, title = message.text.split(None, 1)
        k = await message.reply('Searching Movie/Series in IMDB Database.. 😴')
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await k.edit("No Result.. 😕")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} ({movie.get('year')})",
                    callback_data=f"imdben_{message.from_user.id}_{message.message_id}_{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('Please click button below.. 👇', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Give movie name or series. Ex: <code>/imdb_en soul</code>. 🤷🏻‍♂️')

@Client.on_callback_query(filters.regex('^imdben'))
async def imdb_en_callback(bot: Client, query: CallbackQuery):
    i, user, msg_id, movie = query.data.split('_')
    if user == f"{query.from_user.id}":
      await query.message.edit_text("Permintaan kamu sedang diproses.. ")
      try:
        trl = Translator()
        imdb = await get_poster(query=movie, id=True)
        resp = await get_content(f"https://www.imdb.com/title/tt{movie}/")
        req = requests.get(f"https://betterimdbot.herokuapp.com/?tt=tt{movie}")
        parse = req.json()
        b = BeautifulSoup(resp, "lxml")
        r_json = json.loads(b.find("script", attrs={"type": "application/ld+json"}).contents[0])
        res_str = ""
        if r_json["@type"] == 'Person':
            return query.answer("⚠ Tidak ada hasil ditemukan. Silahkan coba cari manual di Google..", show_alert=True)
        if parse.get("title"):
            res_str += f"<b>📹 Title:</b> <a href='https://www.imdb.com/title/tt{movie}/'>{parse['title']}</a>"
        if parse.get("title_type"):
            res_str += f" ({parse['title_type']})\n"
        else:
            res_str += "\n"
        if imdb.get("kind") == "tv series":
            res_str += f"<b>🍂 Total Season:</b> <code>{imdb['seasons']} season</code>\n"
        if imdb.get("aka"):
            res_str += f"<b>🎤 AKA:</b> <code>{imdb['aka'].split(',')[0]}</code>\n\n"
        else:
            res_str += "\n"
        if parse.get("duration"):
            durasi = parse['duration']
            res_str += f"<b>🕓 Duration:</b> <code>{durasi}</code>\n"
        if r_json.get("contentRating"):
            res_str += f"<b>🔞 Content Rating :</b> <code>{r_json['contentRating']}</code> \n"
        if parse.get("UserRating"):
            user_rating = parse['UserRating']['description']
            res_str += f"<b>⭐ Rating :</b> <code>{user_rating}</code>\n"
        if parse.get("release_date"):
            rilis = parse['release_date']['NAME']
            res_str += f"<b>📆 Release Date :</b> <code>{rilis}</code>\n"
        if parse.get("genres"):
            all_genre = parse['genres']
            genre = "".join(f"{i} " for i in all_genre)
            res_str += f"<b>🔮 Genre :</b> {genre}\n"
        if imdb.get("countries"):
            all_country = imdb['countries']
            if all_country.endswith(", "):
               all_country = all_country[:-2]
            res_str += f"<b>🆔 Country:</b> <code>{all_country}</code>\n"
        if imdb.get("languages"):
            all_lang = imdb['languages']
            if all_lang.endswith(", "):
               all_lang = all_lang[:-2]
            res_str += f"<b>🔊 Language:</b> <code>{all_lang}</code>\n"
        if parse.get("sum_mary"):
            res_str += "\n<b>🙎 Cast Info:</b>\n"
            try:
                director = parse['sum_mary']['Directors']
                director_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in director)
                director_ = director_[:-2]
                res_str += f"<b>Director:</b> {director_}\n"
            except:
                res_str += ""
            try:
                writers = parse['sum_mary']['Writers']
                writers_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in writers)
                writers_ = writers_[:-2]
                res_str += f"<b>Writer:</b> {writers_}\n"
            except:
                res_str += ""
            try:
                stars = parse['sum_mary']['Stars']
                stars_ = "".join(f"<a href='{i['URL']}'>{i['NAME']}</a>, " for i in stars)
                stars_ = stars_[:-2]
                res_str += f"<b>Stars:</b> {stars_}\n"
            except:
                res_str += ""
            res_str += "\n"
        if r_json.get("trailer"):
            trailer_url = "https://imdb.com" + r_json['trailer']['embedUrl']
            markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com/title/tt{movie}/"),
                     InlineKeyboardButton("▶️ Trailer", url=trailer_url)
                    ]
                ])
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Open IMDB", url=f"https://www.imdb.com/title/tt{movie}/")]])
        if imdb.get("plot"):
            try:
              summary = imdb['plot']
              res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
            except Exception:
              res_str += f"<b> 📜 Plot: -</b>\n"
        if r_json.get("keywords"):
            keywords = r_json['keywords'].split(",")
            key_ = ""
            for i in keywords:
                i = i.replace(" ", "_")
                key_ += f"#{i}, "
            key_ = key_[:-2]
            res_str += f"<b>🔥 Keyword/Tags:</b> {key_}\n"
        if parse.get("awards"):
            all_award = parse['awards']
            awards = "".join(f"× {i}\n" for i in all_award)
            res_str += f"<b>🏆 Awards :</b>\n<code> {awards}</code>\n\n"
        else:
            res_str += "\n"
        res_str += f"IMDb Plugin by @MissKatyRoBot"
        thumb = parse.get('poster')
        if thumb:
            try:
                await query.message.reply_photo(photo=thumb, quote=True, caption=res_str, reply_to_message_id=int(msg_id), reply_markup=markup)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = thumb.replace('.jpg', "._V1_UX360.jpg")
                await query.message.reply_photo(photo=poster, caption=res_str, reply_to_message_id=int(msg_id), reply_markup=markup)
            except Exception as e:
                logger.exception(e)
                await query.message.reply(res_str, reply_markup=markup, disable_web_page_preview=False, reply_to_message_id=int(msg_id))
            await query.message.delete()
        else:
            await query.message.edit(res_str, reply_markup=markup, disable_web_page_preview=False)
        await query.answer()
      except Exception as e:
        await query.message.edit_text(f"<b>ERROR:</b>\n<code>{e}</code>")
    else:
        await query.answer("This button not for you..", show_alert=True)
