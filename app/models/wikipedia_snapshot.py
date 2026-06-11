from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class WikipediaSnapshot(Base):
    __tablename__ = "wikipedia_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "page_id",
            "revision_id",
            name="uq_wikipedia_snapshots_company_page_revision",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    page_id = Column(String, nullable=False)
    page_title = Column(String, nullable=False)
    revision_id = Column(String, nullable=False)
    url = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
