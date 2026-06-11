from app.db.database import SessionLocal
from app.models.news_article import NewsArticle
from app.services.data_quality import compact_whitespace
from app.services.data_quality import is_valid_news_article
from app.services.data_quality import normalize_text_key
from app.services.data_quality import normalize_url


def save_news_articles(company_id, articles, source_type="NEWS"):
    db = SessionLocal()

    try:
        saved_count = 0
        seen_titles = set()
        seen_urls = set()

        for article in articles or []:
            title = compact_whitespace(article.get("title"))
            url = normalize_url(
                article.get("link")
                or article.get("url")
            )
            title_key = normalize_text_key(title)

            if not url or not is_valid_news_article(title, url):
                continue

            if title_key in seen_titles or url in seen_urls:
                continue

            seen_titles.add(title_key)
            seen_urls.add(url)

            existing_news = (
                db.query(NewsArticle)
                .filter(
                    NewsArticle.company_id == company_id,
                    NewsArticle.title.ilike(title),
                )
                .first()
            )

            existing_url_news = (
                db.query(NewsArticle)
                .filter(
                    NewsArticle.company_id == company_id,
                    NewsArticle.url == url,
                )
                .first()
            )

            if existing_news or existing_url_news:
                continue

            db.add(
                NewsArticle(
                    company_id=company_id,
                    title=title,
                    url=url,
                    published_at=article.get("published"),
                    source_type=article.get("source_type", source_type),
                )
            )
            saved_count += 1

        db.commit()
        print(f"{saved_count} news articles saved")
        return saved_count

    finally:
        db.close()
