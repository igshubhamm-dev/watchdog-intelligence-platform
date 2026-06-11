from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    category = Column(String, nullable=False)

    run_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    status = Column(String, nullable=False)

    raw_data = Column(JSONB)