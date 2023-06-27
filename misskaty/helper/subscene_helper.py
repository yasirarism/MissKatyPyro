import cloudscraper
from bs4 import BeautifulSoup


async def down_page(url):
    f = cloudscraper.create_scraper()
    resp = f.get(url).text
    soup = BeautifulSoup(resp, "lxml")
    maindiv = soup.body.find("div", class_="subtitle").find("div", class_="top left")
    title = maindiv.find("div", class_="header").h1.span.text.strip()
    try:
        imdb = maindiv.find("div", class_="header").h1.a["href"]
    except TypeError:
        imdb = ""
    try:
        poster = maindiv.find("div", class_="poster").a["href"]
    except:
        poster = ""
    try:
        author_name = (
            maindiv.find("div", class_="header")
            .ul.find("li", class_="author")
            .a.text.strip()
        )
        author_link = f"https://subscene.com{maindiv.find('div', class_='header').ul.find('li', class_='author').a['href']}"
    except:
        author_link = ""
        author_name = "Anonymous"

    download_url = f"https://subscene.com{maindiv.find('div', class_='header').ul.find('li', class_='clearfix').find('div', class_='download').a['href']}"

    try:
        comments = (
            maindiv.find("div", class_="header")
            .ul.find("li", class_="comment-wrapper")
            .find("div", class_="comment")
            .text
        )
    except:
        comments = ""
    try:
        release = (
            maindiv.find("div", class_="header")
            .ul.find("li", class_="release")
            .find_all("div")
        )
        releases = ""
        for i in range(2):
            r = release[i].text.strip()
            releases = f"{releases}\n{r}"
    except Exception:
        releases = ""

    return {
        "title": title,
        "imdb": imdb,
        "poster": poster,
        "author_name": author_name,
        "author_url": author_link,
        "download_url": download_url,
        "comments": comments,
        "releases": releases,
    }
