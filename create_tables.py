from app.db.database import engine, Base

# Import all models 
from app.models.competitor import Competitor
from app.models.company import Company
from app.models.signal_summary import SignalSummary
from app.models.scrape_run import ScrapeRun
from app.models.news_article import NewsArticle
from app.models.briefing import Briefing
from app.models.job_listing import JobListing
from app.models.alert import Alert
from app.models.watchlist import Watchlist
from app.models.personnel import Personnel
from app.models.ad_creative import AdCreative
from app.models.social_post import SocialPost
from app.models.review import Review
from app.models.brand_mention import BrandMention
from app.models.wikipedia_snapshot import WikipediaSnapshot
from app.models.tech_stack_snapshot import TechStackSnapshot

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
