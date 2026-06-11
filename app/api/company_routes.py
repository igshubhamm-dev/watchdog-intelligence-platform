from fastapi import APIRouter
from fastapi import Query

from app.db.database import SessionLocal
from app.models.briefing import Briefing
from app.models.competitor import Competitor
from app.models.company import Company
from app.schemas.company import CompanyRequest

from app.services.intelligence_pipeline import (
    analyze_company_pipeline
)

router = APIRouter()


@router.post("/analyze-company")
def analyze_company(
    request: CompanyRequest
):

    url = request.url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    result = analyze_company_pipeline(
        url
    )

    return result


@router.post("/track")
def track_company(request: CompanyRequest):
    url = request.url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    return analyze_company_pipeline(url)


@router.post("/report")
def generate_report(url: str = Query(...)):
    url = url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    return analyze_company_pipeline(url)


@router.get("/briefing/{company_id}")
def get_latest_briefing(company_id: int):
    db = SessionLocal()

    try:
        briefing = (
            db.query(Briefing)
            .filter(Briefing.company_id == company_id)
            .order_by(Briefing.id.desc())
            .first()
        )

        if not briefing:
            return {}

        return {
            "company_id": briefing.company_id,
            "briefing_md": briefing.briefing_md or briefing.brief,
            "briefing_json": briefing.briefing_json,
            "created_at": briefing.created_at,
        }

    finally:
        db.close()


@router.get("/company/{company_id}")
def get_company(company_id: int):
    db = SessionLocal()

    try:
        company = (
            db.query(Company)
            .filter(Company.id == company_id)
            .first()
        )
        return company or {}

    finally:
        db.close()


@router.get("/competitors/{company_id}")
def get_competitors(company_id: int):

    db = SessionLocal()

    try:

        competitors = (
            db.query(Competitor)
            .filter(
                Competitor.company_id == company_id
            )
            .all()
        )

        return competitors

    finally:

        db.close()
