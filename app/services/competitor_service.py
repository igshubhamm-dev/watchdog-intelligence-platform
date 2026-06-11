from app.db.database import SessionLocal
from app.models.competitor import Competitor
from app.services.data_quality import compact_whitespace
from app.services.data_quality import normalize_text_key


def save_competitors(company_id, competitors):
    db = SessionLocal()

    try:
        saved_count = 0
        seen_names = set()

        for name in competitors or []:
            name = compact_whitespace(name)
            name_key = normalize_text_key(name)

            if not name or name_key in seen_names:
                continue

            seen_names.add(name_key)

            existing_competitor = (
                db.query(Competitor)
                .filter(
                    Competitor.company_id == company_id,
                    Competitor.competitor_name.ilike(name),
                )
                .first()
            )

            if existing_competitor:
                continue

            db.add(
                Competitor(
                    company_id=company_id,
                    competitor_name=name,
                )
            )
            saved_count += 1

        db.commit()
        print(f"{saved_count} competitors saved")
        return saved_count

    finally:
        db.close()
