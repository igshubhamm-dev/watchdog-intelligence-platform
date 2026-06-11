from app.crawlers.news_scraper import search_company_news

news = search_company_news("Stripe")

for item in news:
    print(item)