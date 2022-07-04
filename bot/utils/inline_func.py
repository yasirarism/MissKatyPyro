from pyrogram.types import (InlineKeyboardButton, InlineQueryResultArticle,
                            InputTextMessageContent, InlineKeyboardMarkup)
from bot import arq
import requests, json
from requests.utils import requote_uri

GOOGLE_API = "https://api.abir-hasan.tk/google?query="
YT_API = "https://api.abir-hasan.tk/youtube?query="


async def google_search_func(answers, text):
    results = google(text)
    answers = [
        InlineQueryResultArticle(title=result["title"],
                                 description=result["description"],
                                 input_message_content=InputTextMessageContent(
                                     message_text=result["text"],
                                     disable_web_page_preview=True),
                                 reply_markup=InlineKeyboardMarkup([[
                                     InlineKeyboardButton(text="Buka Website",
                                                          url=result["link"])
                                 ]])) for result in results
    ]
    return answers


async def youtube_func(answers, text):
    results = requests.get(YT_API + requote_uri(text)).json()["result"]
    answers = []
    for result in results:
        title = result["title"]
        views_short = result["viewCount"]["short"]
        duration = result["duration"]
        duration_text = result["accessibility"]["duration"]
        views = result["viewCount"]["text"]
        publishedtime = result["publishedTime"]
        channel_name = result["channel"]["name"]
        channel_link = result["channel"]["link"]
        description = f"{views_short} | {duration}"
        details = f"**Title:** {title}" + "\n" \
        f"**Channel:** [{channel_name}]({channel_link})" + "\n" \
        f"**Duration:** {duration_text}" + "\n" \
        f"**Views:** {views}" + "\n" \
        f"**Published Time:** {publishedtime}" + "\n" \
        "\n" + "**By @MissKatyRoBot**"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Tonton Video 📹",
                                   url=result["link"])]])
        answers.append(
            InlineQueryResultArticle(
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=details),
                reply_markup=reply_markup))
    return answers


async def lyrics_func(answers, text):
    song = await arq.lyrics(text)
    if not song.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=song.result,
                input_message_content=InputTextMessageContent(song.result),
            ))
        return answers
    lyrics = song.result
    song = lyrics.splitlines()
    song_name = song[0]
    artist = song[1]
    if len(lyrics) > 4095:
        lyrics = "**Terlalu Panjang Liriknya**"

    msg = f"__{lyrics}__"

    answers.append(
        InlineQueryResultArticle(
            title=song_name,
            description=artist,
            input_message_content=InputTextMessageContent(msg),
        ))
    return answers


def google(query):
    r = requests.get(GOOGLE_API + requote_uri(query))
    informations = r.json()["results"][:50]
    results = []
    for info in informations:
        text = f"**Judul:** `{info['title']}`"
        text += f"\n**Deskripsi:** `{info['description']}`"
        text += "\n\nBy @MissKatyRoBot"
        results.append({
            "title": info['title'],
            "description": info['description'],
            "text": text,
            "link": info['link']
        })
    return results
