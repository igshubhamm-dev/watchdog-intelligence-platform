from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.sql import func

from app.db.database import Base


class SignalSummary(Base):

    __tablename__ = "signal_summaries"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "signal_type",
            name="uq_signal_summaries_company_type"
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

    signal_type = Column(
        String,
        nullable=False
    )

    summary = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=True
    )

    summary_json = Column(
        JSONB,
        nullable=True
    )

    narrative = Column(
        String,
        nullable=True
    )

    key_changes = Column(
        JSONB,
        nullable=True
    )

    so_what = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
