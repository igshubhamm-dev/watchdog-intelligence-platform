from app.db.database import SessionLocal
from app.models.job_listing import JobListing
from app.services.data_quality import compact_whitespace
from app.services.data_quality import is_valid_job_title
from app.services.data_quality import normalize_text_key
from app.services.data_quality import normalize_url


def save_job_listings(company_id, jobs):
    db = SessionLocal()

    try:
        saved_count = 0
        seen_titles = set()

        for job in jobs or []:
            title = compact_whitespace(job.get("title"))
            title_key = normalize_text_key(title)

            if not is_valid_job_title(title):
                continue

            if title_key in seen_titles:
                continue

            seen_titles.add(title_key)

            existing_job = (
                db.query(JobListing)
                .filter(
                    JobListing.company_id == company_id,
                    JobListing.title.ilike(title),
                )
                .first()
            )

            if existing_job:
                existing_job.job_url = (
                    normalize_url(job.get("url"))
                    or existing_job.job_url
                )
                existing_job.url = existing_job.job_url
                existing_job.location = (
                    compact_whitespace(job.get("location"))
                    or existing_job.location
                )
                existing_job.department = (
                    compact_whitespace(job.get("department"))
                    or existing_job.department
                )
                existing_job.status = "active"
                continue

            job_url = normalize_url(job.get("url"))
            db.add(
                JobListing(
                    company_id=company_id,
                    title=title,
                    job_url=job_url,
                    url=job_url,
                    location=compact_whitespace(job.get("location")),
                    department=compact_whitespace(job.get("department")),
                    status="active",
                )
            )
            saved_count += 1

        db.commit()
        print(f"{saved_count} jobs saved")
        return saved_count

    finally:
        db.close()
