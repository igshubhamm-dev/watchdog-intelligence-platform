from app.db.database import SessionLocal
from app.models.brand_mention import BrandMention
from app.services.data_quality import compact_whitespace
from app.services.data_quality import normalize_url


def save_brand_mentions(company_id, mentions):
    db = SessionLocal()

    try:
        saved_count = 0
        seen = set()

        for mention in mentions or []:
            source = compact_whitespace(mention.get("source"))
            title = compact_whitespace(mention.get("title"))
            url = normalize_url(mention.get("url"))

            if not source or not title or not url:
                continue

            key = (source.casefold(), url)
            if key in seen:
                continue
            seen.add(key)

            existing = (
                db.query(BrandMention)
                .filter(
                    BrandMention.company_id == company_id,
                    BrandMention.source == source,
                    BrandMention.url == url,
                )
                .first()
            )
            if existing:
                continue

            db.add(
                BrandMention(
                    company_id=company_id,
                    source=source,
                    title=title,
                    url=url,
                    author=compact_whitespace(mention.get("author")),
                    score=str(mention.get("score")) if mention.get("score") is not None else None,
                    published_at=mention.get("published_at"),
                    sentiment=compact_whitespace(mention.get("sentiment")),
                )
            )
            saved_count += 1

        db.commit()
        return saved_count

    finally:
        db.close()
