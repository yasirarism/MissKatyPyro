# This plugin to scrape from melongmovie, and lk21
from bs4 import BeautifulSoup
import requests, json, re
from bot import app
from pyrogram import filters
from info import COMMAND_HANDLER

@app.on_message(filters.command(["melongmovie","melongmovie@MissKatyRoBot"], COMMAND_HANDLER))
async def melongmovie(_, message):
     try:
        judul = message.text.split(" ", maxsplit=1)[1]
        msg = await message.reply("Sedang proses scrap, mohon tunggu..")
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
           return await msg.edit('Oops, data film tidak ditemukan di melongmovie')
        res = "".join(f"<b>Judul: {i['judul']}</b>'\n<b>Link</b>: {i['link']}\n\n" for i in data)
        #return await message.reply(json.dumps(data, indent=2, ensure_ascii=False))
        return await msg.edit(res)
     except IndexError:
        return await message.reply("Masukkan kata kunci film yang dicari")
     except Exception as e:
        await message.reply(f"ERROR: {str(e)}")

@app.on_message(filters.command(["lk21","lk21@MissKatyRoBot"], COMMAND_HANDLER) & filters.user(617426792))
async def lk21_scrap(_, message):
    try:
       judul = message.text.split(" ", maxsplit=1)[1]
       msg = await message.reply(f"Mencari film di lk21 dg keyword {judul}..")
       headers = {
           'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
       }

       html = requests.get(judul, headers=headers)
       soup = BeautifulSoup(html.text, 'lxml')
       data = []
       for res in soup.find_all(class_='search-item'):
          link = res.select('a')[0]['href']
          judul = res.select('a')[1]['title']
          try:
             r1 = res.select('a')[2].text
          except:
             r1 = ''
          try:
             r2 = res.select('a')[3].text
          except:
             r2 = ''
          try:
             r3 = res.select('a')[4].text
          except:
             r3 = ''
          try:
             r4 = res.select('a')[5].text
          except:
             r4 = ''
          try:
             r5 = res.select('a')[6].text
          except:
             r5 = ''
          html = requests.get(link)
          soup = BeautifulSoup(html.text, 'lxml')
          dl = soup.find_all(class_='btn btn-primary btn-block')[0]['href']
          soup = BeautifulSoup(html.text, 'lxml')
          data.append({
              'judul': judul,
              'link': link,
              'kualitas': f'{r1} {r2} {r3} {r4} {r5}',
              'dl': dl
          })
       if not data:
          return await msg.edit('Oops, data film tidak ditemukan di LK21')
       res = "".join(f"<b>Judul: {i['judul']}</b>\n<pre>{i['kualitas']}</pre>\n{i['link']}\n<b>Download:</b> <a href='{i['dl']}'>Klik Disini</a>\n\n" for i in data)
       await msg.edit(res)
    except IndexError:
       return await message.reply("Gunakan command /lk21 [judul] untuk search film di lk21 (https://149.56.24.226)")
    except Exception as e:
       await message.reply(f"ERROR: {str(e)}")

@app.on_message(filters.command(["melong","melong@MissKatyRoBot"], COMMAND_HANDLER) & filters.user(617426792))
async def melong_scrap(_, message):
    try:
      judul = message.text.split(" ", maxsplit=1)[1]
      headers = {
          'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
      }

      html = requests.get(judul, headers=headers)
      soup = BeautifulSoup(html.text, 'lxml')
      for ep in soup.findAll(text=re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
          hardsub = ep.findPrevious("div")
          softsub = ep.findNext("div")
          rep = f"{hardsub}\n{softsub}"
          await message.edit(rep)
    except IndexError:
       return await message.reply("Gunakan command /melong <b>[link]</b> untuk scrap link download")
    except Exception as e:
       await message.reply(f"ERROR: {str(e)}")
