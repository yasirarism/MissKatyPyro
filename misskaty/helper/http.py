import re
import urllib.parse
from asyncio import gather
from bs4 import BeautifulSoup
from httpx import AsyncClient, Timeout

# HTTPx Async Client
fetch = AsyncClient(
    verify=False,
    headers={
        "Accept-Language": "en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edge/107.0.1418.42",
    },
    timeout=Timeout(20),
)


async def ddg_search(query: str, max_results: int = 10) -> list[dict]:
    base = "https://html.duckduckgo.com/html/"
    url = f"{base}?q={urllib.parse.quote(query)}"
    resp = await fetch.get(url)
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for result in soup.select(".result"):
        title_tag = result.select_one(".result__title a, .result__a")
        snippet_tag = result.select_one(".result__snippet, .result__excerpt")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        href = title_tag.get("href")
        if not isinstance(href, str) or not href:
            continue
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            href = urllib.parse.unquote(m.group(1))
        else:
            continue
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else "-"
        results.append({"title": title, "link": href, "snippet": snippet})
        if len(results) >= max_results:
            break
    return results


async def get(url: str, *args, **kwargs):
    resp = await fetch.get(url, *args, **kwargs)
    try:
        return await resp.json()
    except Exception:
        return resp.text


async def head(url: str, *args, **kwargs):
    resp = await fetch.head(url, *args, **kwargs)
    try:
        return await resp.json()
    except Exception:
        return resp.text


async def post(url: str, *args, **kwargs):
    resp = await fetch.post(url, *args, **kwargs)
    try:
        return await resp.json()
    except Exception:
        return resp.text


async def multiget(url: str, times: int, *args, **kwargs):
    return await gather(*[get(url, *args, **kwargs) for _ in range(times)])


async def multihead(url: str, times: int, *args, **kwargs):
    return await gather(*[head(url, *args, **kwargs) for _ in range(times)])


async def multipost(url: str, times: int, *args, **kwargs):
    return await gather(*[post(url, *args, **kwargs) for _ in range(times)])


async def resp_get(url: str, *args, **kwargs):
    return await fetch.get(url, *args, **kwargs)


async def resp_post(url: str, *args, **kwargs):
    return await fetch.post(url, *args, **kwargs)
