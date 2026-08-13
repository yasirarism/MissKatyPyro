import logging
from datetime import date

from .http import fetch

LOGGER = logging.getLogger("MissKaty")

IMDB_GRAPHQL_URL = "https://caching.graphql.imdb.com/"
IMDB_GRAPHQL_HEADERS = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "referer": "https://www.imdb.com/",
    "priority": "u=1, i",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Mobile Safari/537.36"
    ),
}
IMDB_TITLE_QUERY = """query GetTitle($id: ID!) {
  title(id: $id) {
    id
    titleText { text }
    originalTitleText { text }
    titleType { text }
    releaseYear { year }
    releaseDate { day month year }
    runtime { seconds }
    ratingsSummary { aggregateRating voteCount }
    spokenLanguages { spokenLanguages { text } }
    countriesOfOrigin { countries { text } }
    certificate { rating }
    genres { genres { text } }
    plot { plotText { plainText } }
    primaryImage { url }
    principalCredits {
      category { text }
      credits { name { id nameText { text } } }
    }
    keywords(first: 10) { edges { node { text } } }
    latestTrailer { playbackURLs { url } }
    metacritic { metascore { score reviewCount } }
    productionBudget { budget { amount currency } }
    openingWeekendGross(boxOfficeArea: DOMESTIC) {
      gross { total { amount currency } }
    }
    domesticGross: lifetimeGross(boxOfficeArea: DOMESTIC) {
      total { amount currency }
    }
    worldwideGross: lifetimeGross(boxOfficeArea: WORLDWIDE) {
      total { amount currency }
    }
    parentsGuide {
      categories {
        category { text }
        severity { text }
      }
    }
    awardNominations(first: 50) {
      total
      edges {
        node {
          isWinner
          award { text }
          category { text }
        }
      }
    }
  }
}"""

_MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def format_imdb_awards(counts: dict | None, locale: str = "en") -> str | None:
    if not counts or not counts.get("total"):
        return None
    wins = counts.get("wins", 0)
    nominations = counts.get("nominations", 0)
    if locale == "id":
        if not wins:
            return f"{nominations} nominasi"
        return f"{wins} kemenangan dari {nominations} nominasi"
    if not wins:
        return f"{nominations} nominations"
    return f"{wins} wins from {nominations} nominations"


def format_imdb_date(raw_date: str | None, locale: str = "id") -> str | None:
    if not raw_date:
        return None
    try:
        year, month, day = [int(part) for part in str(raw_date).split("-")]
        parsed = date(year, month, day)
    except Exception:
        return raw_date
    if locale == "id":
        return f"{parsed.day} {_MONTHS_ID[parsed.month - 1]} {parsed.year}"
    return parsed.strftime("%-d %B %Y")


async def get_imdb_details_graphql(title_id: str):
    title_id = title_id if str(title_id).startswith("tt") else f"tt{title_id}"
    try:
        response = await fetch.post(
            IMDB_GRAPHQL_URL,
            headers=IMDB_GRAPHQL_HEADERS,
            json={
                "query": IMDB_TITLE_QUERY,
                "operationName": "GetTitle",
                "variables": {"id": title_id},
            },
        )
        response.raise_for_status()
        body = response.json()
    except Exception as err:
        LOGGER.warning(f"IMDb GraphQL request failed for {title_id}: {err}")
        return {}

    payload = body.get("data", {}).get("title") or {}
    if not payload:
        if body.get("errors"):
            LOGGER.warning(f"IMDb GraphQL returned errors for {title_id}: {body.get('errors')}")
        return {}

    principal_credits = payload.get("principalCredits") or []

    def _award_counts(award_data):
        total = award_data.get("total") or 0
        wins = sum(
            1
            for edge in award_data.get("edges") or []
            if ((edge.get("node") or {}).get("isWinner") is True)
        )
        return {
            "wins": wins,
            "nominations": max(total - wins, 0),
            "total": total,
        } if total else None

    def _format_awards(award_data):
        counts = _award_counts(award_data)
        if not counts:
            return None
        if not counts["wins"]:
            return f"{counts['nominations']} nominations"
        return f"{counts['wins']} wins from {counts['nominations']} nominations"

    def _money(value):
        money = (value or {}).get("total") or value or {}
        amount = money.get("amount")
        currency = money.get("currency")
        if amount is None or not currency:
            return None
        return {"amount": amount, "currency": currency}

    metacritic = payload.get("metacritic") or {}
    metascore = metacritic.get("metascore") or {}
    budget = ((payload.get("productionBudget") or {}).get("budget") or {})
    guide = []
    for item in (payload.get("parentsGuide") or {}).get("categories") or []:
        category = (item.get("category") or {}).get("text")
        severity = (item.get("severity") or {}).get("text")
        if category:
            guide.append({"category": category, "severity": severity})

    def _people(*categories):
        result = []
        for group in principal_credits:
            category = (group.get("category") or {}).get("text", "")
            if category not in categories:
                continue
            for credit in group.get("credits") or []:
                name_data = credit.get("name") or {}
                name_text = (name_data.get("nameText") or {}).get("text")
                person_id = name_data.get("id")
                if not name_text:
                    continue
                result.append({
                    "@type": "Person",
                    "name": name_text,
                    "url": f"https://www.imdb.com/name/{person_id}/" if person_id else "",
                })
        return result

    release_date = payload.get("releaseDate") or {}
    raw_date = None
    if release_date.get("year"):
        raw_date = f"{release_date.get('year')}-{release_date.get('month') or 1}-{release_date.get('day') or 1}"

    runtime_seconds = (payload.get("runtime") or {}).get("seconds")
    duration_text = f"{runtime_seconds // 60} min" if isinstance(runtime_seconds, int) and runtime_seconds > 0 else None

    return {
        "name": (payload.get("titleText") or {}).get("text"),
        "alternateName": (payload.get("originalTitleText") or {}).get("text"),
        "@type": (payload.get("titleType") or {}).get("text"),
        "releaseYear": (payload.get("releaseYear") or {}).get("year"),
        "datePublished": raw_date,
        "duration": duration_text,
        "inLanguage": [
            (item or {}).get("text")
            for item in (payload.get("spokenLanguages") or {}).get("spokenLanguages", [])
            if (item or {}).get("text")
        ],
        "countryOfOrigin": [
            (item or {}).get("text")
            for item in (payload.get("countriesOfOrigin") or {}).get("countries", [])
            if (item or {}).get("text")
        ],
        "contentRating": (payload.get("certificate") or {}).get("rating"),
        "aggregateRating": {
            "ratingValue": (payload.get("ratingsSummary") or {}).get("aggregateRating"),
            "ratingCount": (payload.get("ratingsSummary") or {}).get("voteCount"),
        },
        "genre": [
            (item or {}).get("text")
            for item in (payload.get("genres") or {}).get("genres", [])
            if (item or {}).get("text")
        ],
        "description": ((payload.get("plot") or {}).get("plotText") or {}).get("plainText"),
        "image": (payload.get("primaryImage") or {}).get("url"),
        "trailer": (
            {"url": ((payload.get("latestTrailer") or {}).get("playbackURLs") or [{}])[0].get("url")}
            if ((payload.get("latestTrailer") or {}).get("playbackURLs") or [{}])[0].get("url")
            else None
        ),
        "keywords": ", ".join(
            (edge.get("node") or {}).get("text")
            for edge in (payload.get("keywords") or {}).get("edges", [])
            if (edge.get("node") or {}).get("text")
        ),
        "director": _people("Director"),
        "creator": _people("Writers", "Writer", "Creator"),
        "actor": _people("Stars", "Cast"),
        "awards": _format_awards(payload.get("awardNominations") or {}),
        "awards_counts": _award_counts(payload.get("awardNominations") or {}),
        "awards_en": _format_awards(payload.get("awardNominations") or {}),
        # Extra fields are consumed only by custom templates; the default
        # renderer intentionally does not read them.
        "metacritic": {
            "score": metascore.get("score"),
            "reviewCount": metascore.get("reviewCount"),
        } if metascore else None,
        "budget": _money(budget),
        "opening": _money(payload.get("openingWeekendGross")),
        "domestic": _money(payload.get("domesticGross")),
        "worldwide": _money(payload.get("worldwideGross")),
        "parents_guide": guide,
    }
