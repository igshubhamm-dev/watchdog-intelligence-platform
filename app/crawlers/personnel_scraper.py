import logging

from bs4 import BeautifulSoup

from app.ai.leadership_analyzer import extract_leadership
from app.services.data_quality import dedupe_records
from app.services.data_quality import is_valid_person_name
from app.services.data_quality import normalize_text_key
from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)


def scrape_personnel(about_page):
    if not about_page:
        return []

    try:
        response = get_url(about_page, timeout=20, retries=2)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        page_text = soup.get_text(separator=" ", strip=True)[:12000]
        personnel = extract_leadership(page_text)
        personnel = [
            person
            for person in personnel
            if is_valid_person_name(person.get("name"))
        ]
        personnel = dedupe_records(
            personnel,
            lambda person: normalize_text_key(person.get("name")),
        )

        print("PERSONNEL FOUND =", len(personnel))
        return personnel[:50]

    except Exception as exc:
        LOGGER.exception("Personnel scraping failed for %s", about_page)
        print(exc)
        return []
