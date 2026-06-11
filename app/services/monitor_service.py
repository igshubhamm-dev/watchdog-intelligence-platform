from app.services.intelligence_pipeline import (
    analyze_company_pipeline
)
from app.db.database import SessionLocal
from app.models.watchlist import Watchlist


def monitor_company(url):

    print(
        f"\nMonitoring: {url}\n"
    )

    result = analyze_company_pipeline(
        url
    )

    print(
        f"\nCompleted: {result['company_name']}"
    )

    return result


def monitor_watchlist():
    db = SessionLocal()

    try:
        companies = db.query(Watchlist).all()
        results = []

        for company in companies:
            results.append(monitor_company(company.website))

        return results

    finally:
        db.close()
