from app.db.database import SessionLocal
from app.models.review import Review
from app.services.data_quality import compact_whitespace


def save_reviews(company_id, reviews):
    db = SessionLocal()

    try:
        saved_count = 0
        seen = set()

        for review in reviews or []:
            source = compact_whitespace(review.get("source"))
            review_text = compact_whitespace(review.get("review_text"))
            review_date = compact_whitespace(review.get("review_date"))

            if not source:
                continue

            key = (source.casefold(), review_text.casefold(), review_date)
            if key in seen:
                continue
            seen.add(key)

            existing = (
                db.query(Review)
                .filter(
                    Review.company_id == company_id,
                    Review.source == source,
                    Review.review_text == review_text,
                    Review.review_date == review_date,
                )
                .first()
            )
            if existing:
                continue

            db.add(
                Review(
                    company_id=company_id,
                    source=source,
                    rating=compact_whitespace(review.get("rating")),
                    review_text=review_text,
                    review_date=review_date,
                )
            )
            saved_count += 1

        db.commit()
        return saved_count

    finally:
        db.close()
