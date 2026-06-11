import logging

from bs4 import BeautifulSoup

from app.services.data_quality import compact_whitespace
from app.services.data_quality import dedupe_records
from app.services.data_quality import normalize_url
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def _platform_for_url(url):
    lowered = (url or "").lower()
    platforms = {
        "linkedin.com": "linkedin",
        "twitter.com": "twitter",
        "x.com": "twitter",
        "instagram.com": "instagram",
        "facebook.com": "facebook",
        "youtube.com": "youtube",
        "tiktok.com": "tiktok",
    }
    for marker, platform in platforms.items():
        if marker in lowered:
            return platform
    return None


def scrape_social_posts(social_links):
    posts = []

    for social_url in social_links or []:
        platform = _platform_for_url(social_url)
        if not platform:
            continue

        try:
            response = get_url(social_url, timeout=12, retries=1)
        except Exception as exc:
            LOGGER.info("Social page fetch failed for %s: %s", social_url, exc)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        title = compact_whitespace(
            soup.title.get_text(" ", strip=True) if soup.title else ""
        )
        description_tag = soup.find("meta", attrs={"property": "og:description"})
        description = compact_whitespace(
            description_tag.get("content") if description_tag else ""
        )

        if not title and not description:
            continue

        posts.append({
            "platform": platform,
            "post_text": description or title,
            "url": normalize_url(social_url),
            "posted_at": None,
            "engagement": None,
        })

    return dedupe_records(posts, lambda item: (item.get("platform"), item.get("url")))
