from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.sql import func

from app.db.database import Base


class Briefing(Base):

    __tablename__ = "briefings"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            name="uq_briefings_company"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    brief = Column(
        String,
        nullable=False
    )

    briefing_md = Column(
        String,
        nullable=True
    )

    briefing_json = Column(
        JSONB,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
