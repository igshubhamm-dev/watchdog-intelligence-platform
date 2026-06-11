from app.crawlers.news_scraper import search_company_news

from app.ai.news_analyzer import analyze_news

from app.ai.briefing_generator import generate_brief


news = search_company_news("Stripe")

summary = analyze_news(news)

brief = generate_brief(summary)

print(brief)