import logging
from urllib.parse import urljoin
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.services.data_quality import dedupe_records
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def _asset_host(asset_url):
    host = urlparse(asset_url).netloc.lower()
    return host.replace("www.", "")


def detect_tech_stack(website_url):
    if not website_url:
        return None

    try:
        response = get_url(website_url, timeout=15, retries=2)
    except Exception as exc:
        LOGGER.exception("Tech stack scrape failed for %s", website_url)
        print("TECH STACK ERROR:", exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    technologies = []
    raw_assets = []

    generator = soup.find("meta", attrs={"name": "generator"})
    if generator and generator.get("content"):
        technologies.append({
            "type": "meta_generator",
            "value": generator.get("content"),
            "evidence": "meta[name=generator]",
        })

    for tag_name, attr_name, asset_type in [
        ("script", "src", "script_host"),
        ("link", "href", "stylesheet_host"),
    ]:
        for tag in soup.find_all(tag_name):
            asset = tag.get(attr_name)
            if not asset:
                continue

            absolute_asset = urljoin(website_url, asset)
            host = _asset_host(absolute_asset)
            if not host:
                continue

            raw_assets.append(absolute_asset)
            technologies.append({
                "type": asset_type,
                "value": host,
                "evidence": absolute_asset,
            })

    technologies = dedupe_records(
        technologies,
        lambda item: (item.get("type"), item.get("value")),
    )

    return {
        "source_url": website_url,
        "technologies": technologies,
        "raw_data": {
            "asset_urls": raw_assets[:100],
        },
    }
