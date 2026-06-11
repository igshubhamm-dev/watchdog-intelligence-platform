from playwright.sync_api import sync_playwright


def fetch_page(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        html = page.content()

        print(
            "HTML LENGTH:",
            len(html)
        )

        browser.close()

        return html