from app.db.database import SessionLocal
from app.models.wikipedia_snapshot import WikipediaSnapshot
from app.services.data_quality import compact_whitespace
from app.services.data_quality import normalize_url


def save_wikipedia_snapshots(company_id, snapshots):
    db = SessionLocal()

    try:
        saved_count = 0

        for snapshot in snapshots or []:
            page_id = str(snapshot.get("page_id") or "")
            revision_id = str(snapshot.get("revision_id") or "")
            page_title = compact_whitespace(snapshot.get("page_title"))

            if not page_id or not revision_id or not page_title:
                continue

            existing = (
                db.query(WikipediaSnapshot)
                .filter(
                    WikipediaSnapshot.company_id == company_id,
                    WikipediaSnapshot.page_id == page_id,
                    WikipediaSnapshot.revision_id == revision_id,
                )
                .first()
            )
            if existing:
                continue

            db.add(
                WikipediaSnapshot(
                    company_id=company_id,
                    page_id=page_id,
                    page_title=page_title,
                    revision_id=revision_id,
                    url=normalize_url(snapshot.get("url")),
                    summary=compact_whitespace(snapshot.get("summary")),
                    raw_data=snapshot.get("raw_data"),
                )
            )
            saved_count += 1

        db.commit()
        return saved_count

    finally:
        db.close()
