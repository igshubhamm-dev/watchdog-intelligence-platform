import logging

from app.utils.http_client import get_url


LOGGER = logging.getLogger(__name__)
API_URL = "https://en.wikipedia.org/w/api.php"


def scrape_wikipedia_snapshot(company_name):
    if not company_name:
        return []

    try:
        search_response = get_url(
            API_URL,
            timeout=15,
            retries=2,
            params={
                "action": "query",
                "list": "search",
                "srsearch": company_name,
                "format": "json",
                "srlimit": 1,
            },
        )
        search_results = search_response.json().get("query", {}).get("search", [])
        if not search_results:
            return []

        page_id = search_results[0].get("pageid")
        page_title = search_results[0].get("title")

        page_response = get_url(
            API_URL,
            timeout=15,
            retries=2,
            params={
                "action": "query",
                "prop": "extracts|info|revisions",
                "pageids": page_id,
                "exintro": 1,
                "explaintext": 1,
                "inprop": "url",
                "rvprop": "ids|timestamp",
                "format": "json",
            },
        )
        payload = page_response.json()
        page = payload.get("query", {}).get("pages", {}).get(str(page_id), {})
        revisions = page.get("revisions") or []
        revision = revisions[0] if revisions else {}

        if not page or not revision.get("revid"):
            return []

        return [{
            "page_id": str(page_id),
            "page_title": page_title,
            "revision_id": str(revision.get("revid")),
            "url": page.get("fullurl"),
            "summary": page.get("extract"),
            "raw_data": page,
        }]

    except Exception as exc:
        LOGGER.exception("Wikipedia scrape failed for %s", company_name)
        print("WIKIPEDIA ERROR:", exc)
        return []
