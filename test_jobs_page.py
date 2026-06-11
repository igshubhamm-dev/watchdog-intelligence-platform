import requests
from bs4 import BeautifulSoup

url = "https://stripe.com/jobs/search"

response = requests.get(
    url,
    headers={
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language":
        "en-US,en;q=0.5"
    }
)

print("Status:", response.status_code)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

for a in soup.find_all("a", href=True):
    text = a.get_text(strip=True)

    if text:
        print(text)