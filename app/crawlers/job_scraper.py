import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.crawlers.greenhouse_scraper import scrape_greenhouse
from app.services.data_quality import compact_whitespace
from app.services.data_quality import dedupe_records
from app.services.data_quality import is_valid_job_title
from app.services.data_quality import normalize_text_key
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)

JOB_URL_HINTS = (
    "/job",
    "/jobs",
    "/careers",
    "/positions",
    "/opening",
    "/openings",
    "lever.co",
    "greenhouse.io",
)


def _has_job_url_hint(href):
    href = (href or "").lower()
    return any(hint in href for hint in JOB_URL_HINTS)


def scrape_jobs(careers_page):
    if not careers_page:
        return []

    try:
        response = get_url(careers_page, timeout=20, retries=2)
        html = response.text

        greenhouse_match = re.search(
            r"boards\.greenhouse\.io/([a-zA-Z0-9_-]+)",
            html,
        )
        if greenhouse_match:
            greenhouse_company = greenhouse_match.group(1)
            print("GREENHOUSE DETECTED:", greenhouse_company)
            return scrape_greenhouse(greenhouse_company)

        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for link in soup.find_all("a", href=True):
            title = compact_whitespace(link.get_text(" ", strip=True))
            href = link.get("href")

            if not href or not _has_job_url_hint(href):
                continue

            if not is_valid_job_title(title):
                continue

            jobs.append({
                "title": title,
                "url": urljoin(careers_page, href),
            })

        unique_jobs = dedupe_records(
            jobs,
            lambda job: normalize_text_key(job.get("title")),
        )

        print("JOBS FOUND =", len(unique_jobs))
        return unique_jobs

    except Exception as exc:
        LOGGER.exception("Job scraping failed for %s", careers_page)
        print(exc)
        return []
