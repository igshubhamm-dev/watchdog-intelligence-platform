from app.db.database import SessionLocal
from app.models.tech_stack_snapshot import TechStackSnapshot
from app.services.data_quality import normalize_url


def save_tech_stack_snapshot(company_id, snapshot):
    if not snapshot:
        return None

    source_url = normalize_url(snapshot.get("source_url"))
    technologies = snapshot.get("technologies") or []

    if not source_url:
        return None

    db = SessionLocal()

    try:
        existing = (
            db.query(TechStackSnapshot)
            .filter(
                TechStackSnapshot.company_id == company_id,
                TechStackSnapshot.source_url == source_url,
            )
            .first()
        )

        if existing:
            existing.technologies = technologies
            existing.raw_data = snapshot.get("raw_data")
            db.commit()
            db.refresh(existing)
            return existing

        record = TechStackSnapshot(
            company_id=company_id,
            source_url=source_url,
            technologies=technologies,
            raw_data=snapshot.get("raw_data"),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    finally:
        db.close()
