from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "source",
            "review_text",
            "review_date",
            name="uq_reviews_company_source_text_date",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    source = Column(String, nullable=False)
    rating = Column(String, nullable=True)
    review_text = Column(String, nullable=True)
    review_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
