from app.db.database import SessionLocal

from app.models.watchlist import Watchlist


def add_company(
    company_name,
    website
):

    db = SessionLocal()

    try:

        existing = (
            db.query(Watchlist)
            .filter(
                Watchlist.website == website
            )
            .first()
        )

        if existing:
            print("Already exists")
            return existing

        company = Watchlist(
            company_name=company_name,
            website=website
        )

        db.add(company)

        db.commit()

        db.refresh(company)

        print("Added")

        return company

    finally:

        db.close()