import logging
from urllib.parse import quote

import feedparser

from app.services.data_quality import compact_whitespace
from app.services.data_quality import dedupe_records
from app.services.data_quality import is_valid_news_article
from app.services.data_quality import normalize_text_key
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def search_company_news(company_name):
    print("NEWS SEARCH:", company_name)

    rss_url = f"https://news.google.com/rss/search?q={quote(company_name)}"

    try:
        response = get_url(rss_url, timeout=12, retries=2)
        feed = feedparser.parse(response.content)
    except Exception as exc:
        LOGGER.exception("News RSS request failed for %s", company_name)
        print("NEWS ERROR:", exc)
        return []

    if getattr(feed, "bozo", False):
        LOGGER.warning(
            "News RSS parse warning for %s: %s",
            company_name,
            getattr(feed, "bozo_exception", "unknown parse error"),
        )

    news_items = []

    for entry in getattr(feed, "entries", [])[:20]:
        title = compact_whitespace(getattr(entry, "title", ""))
        link = getattr(entry, "link", None)

        if not is_valid_news_article(title, link):
            continue

        news_items.append({
            "title": title,
            "link": link,
            "published": getattr(entry, "published", None),
            "source_type": "NEWS",
        })

    return dedupe_records(
        news_items,
        lambda item: (
            item.get("link")
            or normalize_text_key(item.get("title"))
        ),
    )[:10]
