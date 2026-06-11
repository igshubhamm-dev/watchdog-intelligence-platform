from app.crawlers.news_scraper import search_company_news
from app.ai.news_analyzer import analyze_news

news = search_company_news("Stripe")

summary = analyze_news(news)

print(summary)