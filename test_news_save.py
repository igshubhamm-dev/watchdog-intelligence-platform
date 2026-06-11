from app.crawlers.news_scraper import search_company_news
from app.services.scrape_run_service import save_scrape_run


news = search_company_news("Stripe")

run = save_scrape_run(
    company_id=1,
    category="google_news",
    status="success",
    raw_data=news
)

print("Saved Run ID:", run.id)