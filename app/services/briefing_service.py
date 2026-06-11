from app.db.database import SessionLocal
from app.models.briefing import Briefing
from app.services.data_quality import compact_whitespace


def save_briefing(company_id, brief, briefing_json=None):
    db = SessionLocal()

    try:
        brief = compact_whitespace(brief)

        existing_briefing = (
            db.query(Briefing)
            .filter(Briefing.company_id == company_id)
            .first()
        )

        if existing_briefing:
            existing_briefing.brief = brief
            existing_briefing.briefing_md = brief
            existing_briefing.briefing_json = briefing_json
            db.commit()
            db.refresh(existing_briefing)
            return existing_briefing

        record = Briefing(
            company_id=company_id,
            brief=brief,
            briefing_md=brief,
            briefing_json=briefing_json,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()
