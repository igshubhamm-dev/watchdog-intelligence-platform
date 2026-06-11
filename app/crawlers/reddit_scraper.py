import logging
from urllib.parse import quote

from app.services.data_quality import compact_whitespace
from app.services.data_quality import dedupe_records
from app.services.data_quality import normalize_url
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def scrape_reddit_mentions(company_name):
    if not company_name:
        return []

    url = f"https://old.reddit.com/search.json?q={quote(company_name)}&sort=new"

    try:
        response = get_url(url, timeout=15, retries=2)
        payload = response.json()
    except Exception as exc:
        LOGGER.exception("Reddit scrape failed for %s", company_name)
        print("REDDIT ERROR:", exc)
        return []

    mentions = []
    for child in payload.get("data", {}).get("children", [])[:25]:
        data = child.get("data", {})
        title = compact_whitespace(data.get("title"))
        permalink = data.get("permalink")

        if not title or not permalink:
            continue

        mentions.append({
            "source": "reddit",
            "title": title,
            "url": normalize_url(f"https://old.reddit.com{permalink}"),
            "author": data.get("author"),
            "score": data.get("score"),
            "published_at": str(data.get("created_utc")),
        })

    return dedupe_records(mentions, lambda item: item.get("url"))
