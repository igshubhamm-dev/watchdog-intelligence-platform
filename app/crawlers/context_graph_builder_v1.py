import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.crawlers.playwright_crawler import fetch_page


def build_context_graph(url: str):
    html = fetch_page(url)

    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.text.strip() if soup.title else None

    description = None
    meta_desc = soup.find("meta", attrs={"name": "description"})

    if meta_desc:
        description = meta_desc.get("content")

    social_links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if any(domain in href for domain in [
            "linkedin.com",
            "twitter.com",
            "x.com",
            "facebook.com",
            "instagram.com",
            "youtube.com"
        ]):
            social_links.append(href)

    about_page = None
    careers_page = None

    for link in soup.find_all("a", href=True):

        text = link.get_text(strip=True).lower()
        href = urljoin(url, link["href"])

        if "about" in text and not about_page:
            about_page = href

        if any(word in text for word in [
            "careers",
            "career",
            "jobs",
            "join us"
        ]) and not careers_page:
            careers_page = href

    return {
        "website": url,
        "title": title,
        "description": description,
        "social_links": list(set(social_links)),
        "about_page": about_page,
        "careers_page": careers_page
    }