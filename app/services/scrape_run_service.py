from app.db.database import SessionLocal
from app.models.company import Company
from app.models.scrape_run import ScrapeRun


def save_scrape_run(
    company_id,
    category,
    status,
    raw_data
):

    db = SessionLocal()

    try:

        run = ScrapeRun(
            company_id=company_id,
            category=category,
            status=status,
            raw_data=raw_data
        )

        db.add(run)

        db.commit()

        db.refresh(run)

        return run

    finally:
        db.close()