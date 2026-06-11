from app.db.database import SessionLocal
from app.models.job_listing import JobListing

db = SessionLocal()

jobs = db.query(JobListing).filter(
    JobListing.company_id == 3
).all()

print("Total rows:", len(jobs))

titles = set(job.title for job in jobs)

print("Unique titles:", len(titles))