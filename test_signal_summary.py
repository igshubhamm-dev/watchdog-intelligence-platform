from app.crawlers.news_scraper import search_company_news

from app.ai.news_analyzer import analyze_news

from app.services.signal_summary_service import (
    save_signal_summary
)

news = search_company_news("Stripe")

summary = analyze_news(news)

record = save_signal_summary(
    company_id=1,
    signal_type="google_news",
    summary=summary
)

print("Summary Saved")
print("ID:", record.id)