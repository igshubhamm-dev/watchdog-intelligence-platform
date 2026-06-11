from app.db.database import SessionLocal
from app.models.social_post import SocialPost
from app.services.data_quality import compact_whitespace
from app.services.data_quality import normalize_url


def save_social_posts(company_id, posts):
    db = SessionLocal()

    try:
        saved_count = 0
        seen = set()

        for post in posts or []:
            platform = compact_whitespace(post.get("platform"))
            url = normalize_url(post.get("url"))

            if not platform or not url:
                continue

            key = (platform.casefold(), url)
            if key in seen:
                continue
            seen.add(key)

            existing = (
                db.query(SocialPost)
                .filter(
                    SocialPost.company_id == company_id,
                    SocialPost.platform == platform,
                    SocialPost.url == url,
                )
                .first()
            )
            if existing:
                existing.post_text = (
                    compact_whitespace(post.get("post_text"))
                    or existing.post_text
                )
                existing.engagement = post.get("engagement") or existing.engagement
                continue

            db.add(
                SocialPost(
                    company_id=company_id,
                    platform=platform,
                    post_text=compact_whitespace(post.get("post_text")),
                    url=url,
                    posted_at=post.get("posted_at"),
                    engagement=post.get("engagement"),
                )
            )
            saved_count += 1

        db.commit()
        return saved_count

    finally:
        db.close()
