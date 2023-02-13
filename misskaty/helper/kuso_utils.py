import re
import subprocess
import sys

import chevron
import telegraph
import logging
from aiohttp import ClientSession
from misskaty import BOT_USERNAME
from bs4 import BeautifulSoup as bs4

LOGGER = logging.getLogger(__name__)

telegraph = telegraph.Telegraph()
if telegraph.get_access_token() is None:
    token_ph = telegraph.create_account(short_name=BOT_USERNAME)
    LOGGER.info("kuso_utils: Create TGH Account ..")

headers = {"Accept": "*/*", "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}


async def kusonimeBypass(url: str, slug=None):
    hasil = {}
    _url = url
    request = ClientSession(headers=headers)
    if slug:
        noslug_url = "https://kusonime.com/{slug}"
        _url = noslug_url.format({"slug": slug})
    try:
        test = await request.get(_url)
        page = await test.text()
        soup = bs4(page, "html.parser")
        thumb = soup.find("div", {"class": "post-thumb"}).find("img").get("src")
        data = []
        # title = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > p:nth-child(3) > strong")[0].text.strip()
        title = soup.find("h1", {"class": "jdlz"}).text # fix title njing haha
        genre = []
        for _genre in soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(2)"):
            gen = _genre.text.split(":").pop().strip().split(", ")
            genre = gen
        status_anime = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(6)")[0].text.split(":").pop().strip()
        for num, smokedl in enumerate(soup.find("div", {"class": "dlbod"}).find_all("div", {"class": "smokeddl"}), start=1):
            titl = soup.select(f"#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.dlbod > div:nth-child({num}) > div.smokettl")[0].text
            titl = re.sub("Download", "", titl).strip()
            mendata = {"name": titl, "links": []}
            for smokeurl in smokedl.find_all("div", {"class": "smokeurl"}):
                quality = smokeurl.find("strong").text
                links = []
                for link in smokeurl.find_all("a"):
                    url = link.get("href")
                    client = link.text
                    links.append({"client": client, "url": url})
                mendata["links"].append(dict(quality=quality, link_download=links))
            data.append(mendata)
        hasil |= {
            "error": False,
            "title": title,
            "thumb": thumb,
            "genre": genre,
            "genre_string": ", ".join(genre),
            "status_anim": status_anime,
            "data": data,
        }
    except:
        hasil |= {"error": True, "error_message": "kuso bypass error"}
    finally:
        await request.close()
        return hasil


async def byPassPh(url: str, msg_id: int):
    kusonime = await kusonimeBypass(url)
    results = {"error": True, "error_message": "Post to or create TGH error"}
    if not kusonime["error"]:
        template = """
<img src={{{thumb}}}>
<p><b>Title</b> : <code>{{title}}</code></p>
<p><b>Genre</b> : <code>{{genre_string}}</code></p>
<p><b>Status</b> : <code>{{status_anime}}</code></p>
<br>
{{#data}}
    <h4>{{name}}</h4>
    {{#links}}
    <p><b>Resolution: {{quality}}</b></p>
    {{#link_download}}
    <p>✗ <a href="{{url}}">{{client}}</a></p>
    {{/link_download}}
    {{/links}}
    <br>
{{/data}}
""".strip()
        html = chevron.render(template, kusonime)
        page = telegraph.create_page(f"{kusonime.get('title')}-{msg_id}", html_content=html)
        results |= {"error": False, "url": f'https://telegra.ph/{page["path"]}'}
        del results["error_message"]
    return results


class Kusonime:
    def __init__(self):
        pass

    async def byPass(self, url):
        return await kusonimeBypass(url)

    async def telegraph(self, url, msg_id):
        return await byPassPh(url, msg_id)