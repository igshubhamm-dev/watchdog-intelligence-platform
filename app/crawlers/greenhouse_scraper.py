from bs4 import BeautifulSoup

from app.services.data_quality import compact_whitespace
from app.services.data_quality import dedupe_records
from app.services.data_quality import is_valid_job_title
from app.services.data_quality import normalize_text_key
from app.utils.http_client import get_url


def scrape_greenhouse(company):

    url = (
        f"https://boards.greenhouse.io/{company}"
    )

    try:

        response = get_url(url, timeout=20, retries=2)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        jobs = []

        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link.get("href")
            text = compact_whitespace(link.get_text(strip=True))

            if not href:
                continue

            # Greenhouse job links
            if "/jobs/" not in href:
                continue

            if not is_valid_job_title(text):
                continue

            jobs.append({
                "title": text,
                "url": link["href"]
            })

        jobs = dedupe_records(
            jobs,
            lambda job: normalize_text_key(job.get("title"))
        )

        print("GREENHOUSE JOBS:", len(jobs))

        return jobs

    except Exception as e:

        print(e)

        return []
    
