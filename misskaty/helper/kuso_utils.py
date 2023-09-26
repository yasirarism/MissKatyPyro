import logging
import traceback
from html import escape

import chevron
from bs4 import BeautifulSoup
from telegraph.aio import Telegraph
from typing import Optional

from misskaty import BOT_USERNAME
from misskaty.helper.http import fetch
from misskaty.helper.media_helper import post_to_telegraph

LOGGER = logging.getLogger("MissKaty")


async def kusonimeBypass(url: str):
    result = {}
    page = await fetch.get(url)
    if page.status_code != 200:
        raise Exception(f"ERROR: Hostname might be blocked by server!")
    try:
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
            if not smokedl:
                continue
            mendata = {"name": title, "links": []}
            for smokeurl in smokedl.find_all("div", {"class": "smokeurl"}):
                if not smokeurl:
                    continue
                quality = smokeurl.find("strong").text
                links = []
                for link in smokeurl.find_all("a"):
                    url = link.get("href")
                    client = link.text
                    links.append({"client": client, "url": url})
                mendata["links"].append({"quality": quality, "link_download": links})
            for smokeurl in smokedl.find_all("div", {"class": "smokeurlrh"}):
                if not smokeurl:
                    continue
                quality = smokeurl.find("strong").text
                links = []
                for link in smokeurl.find_all("a"):
                    url = link.get("href")
                    client = link.text
                    links.append({"client": client, "url": url})
                mendata["links"].append({"quality": quality, "link_download": links})
            data.append(mendata)
            num += 1
        for smokedl in soup.find("div", {"class": "dlbodz"}).find_all("div", {"class": "smokeddl"}):
            if not smokedl:
                continue
            mendata = {"name": title, "links": []}
            for smokeurl in smokedl.find_all("div", {"class": "smokeurl"}):
                if not smokeurl:
                    continue
                quality = smokeurl.find("strong").text
                links = []
                for link in smokeurl.find_all("a"):
                    url = link.get("href")
                    client = link.text
                    links.append({"client": client, "url": url})
                mendata["links"].append({"quality": quality, "link_download": links})
            for smokeurl in smokedl.find_all("div", {"class": "smokeurlrh"}):
                if not smokeurl:
                    continue
                quality = smokeurl.find("strong").text
                links = []
                for link in smokeurl.find_all("a"):
                    url = link.get("href")
                    client = link.text
                    links.append({"client": client, "url": url})
                mendata["links"].append({"quality": quality, "link_download": links})
            data.append(mendata)
            num += 1
        result.update({"title": title, "thumb": thumb, "genre": genre, "genre_string": ", ".join(genre), "status_anime": status_anime, "season": season, "tipe": tipe, "ep": ep, "score": score, "duration": duration, "rilis": rilis, "data": data})
    except Exception as e:
        if len(result) != 0:
            result.clear()
        err = traceback.format_exc()
        LOGGER.error(f"class: {e.__class__.__name_}, {err}")
        raise Exception(f"ERROR: {err}")
    finally:
        return result


async def byPassPh(url: str, name: str) -> Optional[str]:
    kusonime = await kusonimeBypass(url)
    if not isinstance(kusonime, dict):
        return kusonime
    template = """
<img src={{{thumb}}}>

<p><b>Title</b> : <code>{{title}}</code></p>
<p><b>Genre</b> : <code>{{genre_string}}</code></p>
<br><p><b>Season</b> : <code>{{season}}</code></p>
<br><p><b>Type</b> : <code>{{tipe}}</code></p>
<br><p><b>Status</b> : <code>{{status_anime}}</code></p>
<br><p><b>Total Episode</b> : <code>{{ep}}</code></p>
<br><p><b>Score</b> : <code>{{score}}</code></p>
<br><p><b>Duration</b> : <code>{{duration}}</code></p>
<br><p><b>Released on</b> : <code>{{rilis}}</code></p>
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
    plink = await post_to_telegraph(
        False, f"{kusonime.get('title')} By {escape(name)}", chevron.render(template, kusonime)
    )
    return plink


class Kusonime:
    def __init__(self):  # skipcq
        pass

    @staticmethod
    async def byPass(url):
        return await kusonimeBypass(url)

    @staticmethod
    async def telegraph(url, name):
        return await byPassPh(url, name)
