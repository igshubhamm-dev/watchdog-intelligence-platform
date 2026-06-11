from app.db.database import SessionLocal
from app.models.ad_creative import AdCreative
from app.services.data_quality import compact_whitespace


def save_ad_creatives(company_id, ads):
    db = SessionLocal()

    try:
        saved_count = 0
        seen = set()

        for ad in ads or []:
            platform = compact_whitespace(ad.get("platform"))
            ad_text = compact_whitespace(ad.get("ad_text"))

            if not platform or not ad_text:
                continue

            key = (platform.casefold(), ad_text.casefold())
            if key in seen:
                continue
            seen.add(key)

            existing = (
                db.query(AdCreative)
                .filter(
                    AdCreative.company_id == company_id,
                    AdCreative.platform == platform,
                    AdCreative.ad_text == ad_text,
                )
                .first()
            )
            if existing:
                existing.ended_at = ad.get("ended_at") or existing.ended_at
                existing.spend_range = ad.get("spend_range") or existing.spend_range
                continue

            db.add(
                AdCreative(
                    company_id=company_id,
                    platform=platform,
                    ad_text=ad_text,
                    image_url_desc=compact_whitespace(ad.get("image_url_desc")),
                    started_at=ad.get("started_at"),
                    ended_at=ad.get("ended_at"),
                    spend_range=ad.get("spend_range"),
                )
            )
            saved_count += 1

        db.commit()
        return saved_count

    finally:
        db.close()
