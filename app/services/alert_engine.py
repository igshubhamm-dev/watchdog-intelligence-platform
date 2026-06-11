from app.db.database import SessionLocal
from app.models.job_listing import JobListing
from app.services.alert_service import save_alert
from app.services.data_quality import is_valid_job_title
from app.services.data_quality import normalize_text_key


def detect_new_jobs(company_id, current_jobs):
    db = SessionLocal()

    try:
        print("Running alert detection...")

        existing_jobs = (
            db.query(JobListing)
            .filter(JobListing.company_id == company_id)
            .all()
        )

        existing_titles = {
            normalize_text_key(job.title)
            for job in existing_jobs
        }

        print(f"Unique existing titles: {len(existing_titles)}")
        print(f"Current jobs: {len(current_jobs or [])}")
        print(f"Existing jobs: {len(existing_titles)}")

        for job in current_jobs or []:
            title = job.get("title")
            title_key = normalize_text_key(title)

            if not is_valid_job_title(title):
                continue

            if title_key not in existing_titles:
                print(f"NEW JOB FOUND: {title}")
                save_alert(
                    company_id=company_id,
                    alert_type="NEW_JOB",
                    message=f"New job detected: {title}",
                )
                existing_titles.add(title_key)
                print(f"ALERT: {title}")

    finally:
        db.close()
