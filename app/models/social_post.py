from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class SocialPost(Base):
    __tablename__ = "social_posts"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "platform",
            "url",
            name="uq_social_posts_company_platform_url",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    platform = Column(String, nullable=False)
    post_text = Column(String, nullable=True)
    url = Column(String, nullable=False)
    posted_at = Column(String, nullable=True)
    engagement = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
