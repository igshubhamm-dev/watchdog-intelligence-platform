import logging
from urllib.parse import urljoin
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import feedparser

from app.services.data_quality import compact_whitespace
from app.services.data_quality import dedupe_records
from app.services.data_quality import is_valid_news_article
from app.services.data_quality import normalize_url
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)

IGNORED_TITLES = {
    "home",
    "login",
    "sign in",
    "contact",
    "privacy",
    "terms",
    "subscribe",
    "skip to main content",
}

IGNORED_URL_ENDINGS = [
    "/blog/",
    "/news/",
    "/product-updates/",
    "/design-systems/",
    "/behind-the-scenes/",
    "/career-and-education/",
    "/product-management/",
    "/accessibility/",
]


def is_likely_article(title, post_url):
    normalized_title = title.strip().lower()
    normalized_url = post_url.lower()
    path = urlparse(post_url).path
    normalized_path = path.lower()
    path_with_slash = normalized_path.rstrip("/") + "/"

    if normalized_title in IGNORED_TITLES:
        return False

    if not is_valid_news_article(title, post_url):
        return False

    if "/blog/" not in normalized_url and "/news/" not in normalized_url:
        return False

    if any(path_with_slash.endswith(ending) for ending in IGNORED_URL_ENDINGS):
        return False

    return True


def article_priority(post_url):
    path_segments = [
        segment
        for segment in urlparse(post_url).path.split("/")
        if segment
    ]

    if len(path_segments) >= 4:
        return 0

    return 1


def scrape_blog_posts(page_url):
    if not page_url:
        return []

    try:
        response = get_url(page_url, timeout=20, retries=2)

        content_type = response.headers.get("content-type", "").lower()
        if (
            "xml" in content_type
            or "rss" in content_type
            or page_url.endswith((".xml", "/feed", "/rss"))
        ):
            feed = feedparser.parse(response.content)
            posts = []
            for entry in getattr(feed, "entries", [])[:20]:
                title = compact_whitespace(getattr(entry, "title", ""))
                post_url = normalize_url(getattr(entry, "link", None))
                if not post_url or not is_valid_news_article(title, post_url):
                    continue
                posts.append({
                    "title": title,
                    "url": post_url,
                    "published": getattr(entry, "published", None),
                    "summary": compact_whitespace(getattr(entry, "summary", "")),
                    "source_type": "BLOG",
                })
            return dedupe_records(posts, lambda post: post.get("url"))

        soup = BeautifulSoup(response.text, "html.parser")

        candidates = []

        for link in soup.find_all("a", href=True):
            title = compact_whitespace(link.get_text(separator=" ", strip=True))
            if not title:
                continue

            post_url = normalize_url(urljoin(page_url, link["href"]))

            if not is_likely_article(title, post_url):
                continue

            candidates.append({
                "title": title,
                "url": post_url,
                "source_type": "BLOG",
            })

        candidates = dedupe_records(
            candidates,
            lambda post: post.get("url"),
        )
        candidates = sorted(
            candidates,
            key=lambda post: article_priority(post["url"]),
        )

        posts = candidates[:20]
        print("BLOG POSTS FOUND =", len(posts))
        return posts

    except Exception as exc:
        LOGGER.exception("Blog scraping failed for %s", page_url)
        return []
