from app.db.database import SessionLocal
from app.models.personnel import Personnel
from app.services.data_quality import compact_whitespace
from app.services.data_quality import is_valid_person_name
from app.services.data_quality import normalize_text_key


def save_personnel(company_id, personnel_list):
    db = SessionLocal()

    try:
        saved_count = 0
        seen_names = set()

        for person in personnel_list or []:
            name = compact_whitespace(person.get("name"))
            name_key = normalize_text_key(name)

            if not is_valid_person_name(name):
                continue

            if name_key in seen_names:
                continue

            seen_names.add(name_key)

            existing_person = (
                db.query(Personnel)
                .filter(
                    Personnel.company_id == company_id,
                    Personnel.name.ilike(name),
                )
                .first()
            )

            if existing_person:
                existing_person.role = (
                    compact_whitespace(person.get("role"))
                    or existing_person.role
                )
                existing_person.title = (
                    compact_whitespace(person.get("title"))
                    or compact_whitespace(person.get("role"))
                    or existing_person.title
                )
                existing_person.linkedin_url = (
                    person.get("linkedin_url")
                    or existing_person.linkedin_url
                )
                existing_person.status = "active"
                continue

            title = (
                compact_whitespace(person.get("title"))
                or compact_whitespace(person.get("role"))
            )
            db.add(
                Personnel(
                    company_id=company_id,
                    name=name,
                    role=title,
                    title=title,
                    linkedin_url=person.get("linkedin_url"),
                    status="active",
                )
            )
            saved_count += 1

        db.commit()
        print(f"{saved_count} personnel saved")
        return saved_count

    finally:
        db.close()
