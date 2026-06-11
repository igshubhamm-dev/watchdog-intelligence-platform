import re
from urllib.parse import urlparse

from app.db.database import SessionLocal
from app.models.company import Company


def _normalize_name_key(value):
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def clean_company_name(title, url=None):
    if not title:
        return "Unknown"

    separators = ["|", "-", ":", "·", "Â·"]
    pattern = "|".join(re.escape(sep) for sep in separators)
    name_parts = [
        part.strip()
        for part in re.split(pattern, title)
        if part.strip()
    ]
    name = name_parts[0] if name_parts else title

    if url:
        domain = urlparse(url).netloc.replace("www.", "")
        domain_key = _normalize_name_key(domain.split(".")[0])

        for part in name_parts:
            part_key = _normalize_name_key(part)

            if domain_key and (
                domain_key in part_key
                or part_key in domain_key
            ):
                name = part
                break

    name = re.sub(
        r"\s+(India|IN|Official Website)$",
        "",
        name,
        flags=re.IGNORECASE,
    )

    return name.strip()


def save_company(url, context_graph):
    db = SessionLocal()

    try:
        existing_company = (
            db.query(Company)
            .filter(Company.url == url)
            .first()
        )

        if existing_company:
            existing_company.name = clean_company_name(
                context_graph.get("title"),
                url,
            )
            existing_company.context_graph = context_graph

            db.commit()
            db.refresh(existing_company)

            print("Company updated")

            return existing_company

        company = Company(
            url=url,
            name=clean_company_name(
                context_graph.get("title"),
                url,
            ),
            context_graph=context_graph,
        )

        db.add(company)

        db.commit()

        db.refresh(company)

        print("Company created")

        return company

    finally:
        db.close()
