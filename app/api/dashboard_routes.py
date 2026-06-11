from fastapi import APIRouter

from app.db.database import SessionLocal

from app.models.company import Company
from app.models.alert import Alert
from app.models.job_listing import JobListing
from app.models.news_article import NewsArticle
from app.models.briefing import Briefing
from app.models.personnel import Personnel
from app.models.competitor import Competitor
from app.models.ad_creative import AdCreative
from app.models.brand_mention import BrandMention
from app.models.review import Review
from app.models.social_post import SocialPost
from app.models.tech_stack_snapshot import TechStackSnapshot
from app.models.wikipedia_snapshot import WikipediaSnapshot

router = APIRouter()


@router.get("/companies")
def get_companies():

    db = SessionLocal()

    try:

        companies = db.query(
            Company
        ).all()

        return companies

    finally:

        db.close()


@router.get("/personnel/{company_id}")
def get_personnel(company_id: int):

    db = SessionLocal()

    try:

        personnel = (
            db.query(Personnel)
            .filter(
                Personnel.company_id == company_id
            )
            .all()
        )

        return personnel

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


@router.get("/alerts")
def get_alerts():

    db = SessionLocal()

    try:

        alerts = db.query(
            Alert
        ).order_by(
            Alert.id.desc()
        ).all()

        return alerts

    finally:

        db.close()


@router.get("/jobs/{company_id}")
def get_jobs(company_id: int):

    db = SessionLocal()

    try:

        jobs = (
            db.query(JobListing)
            .filter(
                JobListing.company_id == company_id
            )
            .all()
        )

        return jobs

    finally:

        db.close()


@router.get("/news/{company_id}")
def get_news(company_id: int):

    db = SessionLocal()

    try:

        news = (
            db.query(NewsArticle)
            .filter(
                NewsArticle.company_id == company_id
            )
            .all()
        )

        return news

    finally:

        db.close()


@router.get("/briefings/{company_id}")
def get_briefings(company_id: int):

    db = SessionLocal()

    try:

        briefings = (
            db.query(Briefing)
            .filter(
                Briefing.company_id == company_id
            )
            .all()
        )

        return briefings

    finally:

        db.close()


@router.get("/alerts/{company_id}")
def get_company_alerts(company_id: int):

    db = SessionLocal()

    try:

        alerts = (
            db.query(Alert)
            .filter(
                Alert.company_id == company_id
            )
            .order_by(
                Alert.id.desc()
            )
            .all()
        )

        return alerts

    finally:

        db.close()


@router.get("/technology-stack/{company_id}")
def get_technology_stack(company_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(TechStackSnapshot)
            .filter(TechStackSnapshot.company_id == company_id)
            .order_by(TechStackSnapshot.id.desc())
            .all()
        )

    finally:
        db.close()


@router.get("/reviews/{company_id}")
def get_reviews(company_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(Review)
            .filter(Review.company_id == company_id)
            .order_by(Review.id.desc())
            .all()
        )

    finally:
        db.close()


@router.get("/wikipedia/{company_id}")
def get_wikipedia(company_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(WikipediaSnapshot)
            .filter(WikipediaSnapshot.company_id == company_id)
            .order_by(WikipediaSnapshot.id.desc())
            .all()
        )

    finally:
        db.close()


@router.get("/social-posts/{company_id}")
def get_social_posts(company_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(SocialPost)
            .filter(SocialPost.company_id == company_id)
            .order_by(SocialPost.id.desc())
            .all()
        )

    finally:
        db.close()


@router.get("/brand-mentions/{company_id}")
def get_brand_mentions(company_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(BrandMention)
            .filter(BrandMention.company_id == company_id)
            .order_by(BrandMention.id.desc())
            .all()
        )

    finally:
        db.close()


@router.get("/ad-creatives/{company_id}")
def get_ad_creatives(company_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(AdCreative)
            .filter(AdCreative.company_id == company_id)
            .order_by(AdCreative.id.desc())
            .all()
        )

    finally:
        db.close()
