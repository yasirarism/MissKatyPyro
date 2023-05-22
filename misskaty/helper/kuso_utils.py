import re

import chevron
from telegraph.aio import Telegraph
import logging
from misskaty.helper.http import http
from misskaty import BOT_USERNAME
from bs4 import BeautifulSoup as bs4

LOGGER = logging.getLogger(__name__)

headers = {"Accept": "*/*", "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}


async def kusonimeBypass(url: str, slug=None):
    result = {}
    _url = url
    if slug:
        noslug_url = "https://kusonime.com/{slug}"
        _url = noslug_url.format({"slug": slug})
    try:
        page = await http.get(_url, headers=headers)
        soup = BeautifulSoup(page.text, "lxml")
        thumb = soup.find("div", {"class": "post-thumb"}).find("img").get("src")
        data = []
        # title = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > p:nth-child(3) > strong")[0].text.strip()
        try:
            title = soup.find("h1", {"class": "jdlz"}).text  # fix title njing haha
            season = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(3)")[0].text.split(":").pop().strip()
            tipe = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(5)")[0].text.split(":").pop().strip()
            status_anime = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(6)")[0].text.split(":").pop().strip()
            ep = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(7)")[0].text.split(":").pop().strip()
            score = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(8)")[0].text.split(":").pop().strip()
            duration = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(9)")[0].text.split(":").pop().strip()
            rilis = soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(10)")[0].text.split(":").pop().strip()
        except Exception:
            e = traceback.format_exc()
            LOGGER.error(e)
            title, season, tipe, status_anime, ep, score, duration, rilis = "None", "None", "None", "None", 0, 0, 0, "None"
        num = 1
        genre = []
        for _genre in soup.select("#venkonten > div.vezone > div.venser > div.venutama > div.lexot > div.info > p:nth-child(2)"):
            gen = _genre.text.split(":").pop().strip().split(", ")
            genre = gen
        for smokedl in soup.find("div", {"class": "dlbodz"}).find_all("div", {"class": "smokeddlrh"}):
            mendata = {"name": title, "links": []}
            for smokeurl in smokedl.find_all("div", {"class": "smokeurlrh"}):
                quality = smokeurl.find("strong").text
                links = []
                for link in smokeurl.find_all("a"):
                    url = link.get("href")
                    client = link.text
                    links.append({"client": client, "url": url})
                mendata["links"].append({"quality": quality, "link_download": links})
            data.append(mendata)
            num += 1
        result.update({"error": False, "title": title, "thumb": thumb, "genre": genre, "genre_string": ", ".join(genre), "status_anime": status_anime, "season": season, "tipe": tipe, "ep": ep, "score": score, "duration": duration, "rilis": rilis, "data": data})
    except Exception:
        err = traceback.format_exc()
        LOGGER.error(err)
        result.update({"error": True, "error_message": err})
    finally:
        LOGGER.info(result)
        await http.delete(_url)
        return result


async def byPassPh(url: str, name: str):
    kusonime = await kusonimeBypass(url)
    results = {"error": True, "error_message": kusonime}
    template = """
<img src={{{thumb}}}>

<p><b>Title</b> : <code>{{title}}</code></p>
<p><b>Genre</b> : <code>{{genre_string}}</code></p>
<br><br><p><b>Season</b> : <code>{{season}}</code></p>
<br><br><p><b>Type</b> : <code>{{tipe}}</code></p>
<br><br><p><b>Status</b> : <code>{{status_anime}}</code></p>
<br><br><p><b>Total Episode</b> : <code>{{ep}}</code></p>
<br><br><p><b>Score</b> : <code>{{score}}</code></p>
<br><br><p><b>Duration</b> : <code>{{duration}}</code></p>
<br><br><p><b>Released on</b> : <code>{{rilis}}</code></p>
<br><br>
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
    LOGGER.info(kusonime)
    if not kusonime["error"]:
        html = render(template, kusonime)
        telegraph = Telegraph()
        if not telegraph.get_access_token():
            await telegraph.create_account(short_name=bot_name)
        page = await telegraph.create_page(f"{kusonime.get('title')} By {escape(name)}", html_content=html)
        results.update({"error": False, "url": "https://telegra.ph/{}".format(page["path"])})
        del results["error_message"]
    return results


class Kusonime:
    def __init__(self):
        pass

    async def byPass(self, url):
        return await kusonimeBypass(url)

    async def telegraph(self, url, name):
        return await byPassPh(url, name)
