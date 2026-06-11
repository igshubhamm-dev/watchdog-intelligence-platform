import logging
from urllib.parse import urljoin
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def _same_site(base_url, candidate_url):
    base_host = urlparse(base_url).netloc.replace("www.", "")
    candidate_host = urlparse(candidate_url).netloc.replace("www.", "")
    return bool(candidate_host) and candidate_host == base_host


def _first_matching_page(soup, base_url, words):
    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True).lower()
        href = urljoin(base_url, link["href"])

        if not _same_site(base_url, href):
            continue

        if any(word in text for word in words):
            return href

    return None


def _probe_paths(base_url, paths):
    for path in paths:
        candidate = base_url.rstrip("/") + path

        try:
            response = get_url(candidate, timeout=8, retries=1)
        except Exception as exc:
            LOGGER.info("Context probe failed for %s: %s", candidate, exc)
            continue

        if response.status_code == 200:
            return candidate

    return None


def build_context_graph(url: str):
    try:
        response = get_url(url, timeout=20, retries=2)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.get_text(" ", strip=True) if soup.title else None

        if title and any(
            marker in title.lower()
            for marker in [
                "403",
                "forbidden",
                "504",
                "502",
                "access denied",
            ]
        ):
            raise ValueError("Invalid website response")

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content") if meta_desc else None

        social_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if any(
                domain in href
                for domain in [
                    "linkedin.com",
                    "twitter.com",
                    "x.com",
                    "facebook.com",
                    "instagram.com",
                    "youtube.com",
                    "tiktok.com",
                ]
            ):
                social_links.append(urljoin(url, href))

        rss_feed_url = None
        for link in soup.find_all("link", href=True):
            rel = " ".join(link.get("rel", [])).lower()
            link_type = (link.get("type") or "").lower()
            if "alternate" in rel and (
                "rss" in link_type
                or "atom" in link_type
            ):
                rss_feed_url = urljoin(url, link["href"])
                break

        about_page = _first_matching_page(
            soup,
            url,
            ["about", "company", "team", "leadership"],
        ) or _probe_paths(
            url,
            ["/about", "/about-us", "/company", "/our-story", "/team", "/leadership"],
        )

        careers_page = _first_matching_page(
            soup,
            url,
            ["careers", "career", "jobs", "join us"],
        ) or _probe_paths(
            url,
            ["/careers", "/jobs", "/join-us", "/work-with-us"],
        )

        blog_page = _first_matching_page(
            soup,
            url,
            ["blog", "insights"],
        ) or _probe_paths(url, ["/blog", "/insights"])

        news_page = _first_matching_page(
            soup,
            url,
            ["news", "newsroom"],
        ) or _probe_paths(url, ["/news", "/newsroom"])

        press_page = _first_matching_page(
            soup,
            url,
            ["press", "media"],
        ) or _probe_paths(url, ["/press", "/media"])

        if not rss_feed_url:
            rss_feed_url = _probe_paths(
                url,
                ["/feed", "/rss", "/atom.xml", "/blog/feed"],
            )

        wikipedia_url = None
        crunchbase_url = None
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "wikipedia.org/wiki/" in href and not wikipedia_url:
                wikipedia_url = href
            if "crunchbase.com/organization/" in href and not crunchbase_url:
                crunchbase_url = href

        return {
            "website": url,
            "title": title,
            "description": description,
            "social_links": sorted(set(social_links)),
            "about_page": about_page,
            "careers_page": careers_page,
            "careers_pages": [careers_page] if careers_page else [],
            "blog_page": blog_page,
            "rss_feed_url": rss_feed_url,
            "news_page": news_page,
            "press_page": press_page,
            "wikipedia_url": wikipedia_url,
            "crunchbase_url": crunchbase_url,
        }

    except Exception as exc:
        LOGGER.exception("Context graph failed for %s", url)
        return {
            "website": url,
            "title": None,
            "description": str(exc),
            "social_links": [],
            "about_page": None,
            "careers_page": None,
            "careers_pages": [],
            "blog_page": None,
            "rss_feed_url": None,
            "news_page": None,
            "press_page": None,
            "wikipedia_url": None,
            "crunchbase_url": None,
        }
