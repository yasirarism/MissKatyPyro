from bs4 import BeautifulSoup
import requests, json
from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER

@app.on_message(filters.command(["melongmovie","melongmovie@MissKatyRoBot"], COMMAND_HANDLER))
async def melongmovie(_, message):
     try:
        judul = message.text.split(" ", maxsplit=1)[1]
        headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        html = requests.get(f'http://167.99.31.48/?s={judul}', headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')
        data = []
        for res in soup.select('.box'):
           dd = res.select("a")
           url = dd[0]['href']
           title = dd[0]['title']
           kualitas = dd[0].find(class_="quality").text
           data.append({
               'judul': title,
               'link': url,
               'kualitas': kualitas
           })
        if not data:
           return await message.reply('Oops, data film tidak ditemukan di melongmovie')
        return await message.reply(json.dumps(data, indent=2, ensure_ascii=False))
     except IndexError:
        await message.reply("Masukkan kata kunci film yang dicari")
