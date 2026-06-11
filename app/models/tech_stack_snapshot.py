from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class TechStackSnapshot(Base):
    __tablename__ = "tech_stack_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "source_url",
            name="uq_tech_stack_snapshots_company_source",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    source_url = Column(String, nullable=False)
    technologies = Column(JSONB, nullable=False)
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
