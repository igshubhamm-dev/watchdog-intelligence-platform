from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class BrandMention(Base):
    __tablename__ = "brand_mentions"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "source",
            "url",
            name="uq_brand_mentions_company_source_url",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    author = Column(String, nullable=True)
    score = Column(String, nullable=True)
    published_at = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
