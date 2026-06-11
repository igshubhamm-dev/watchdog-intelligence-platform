from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import UniqueConstraint

from sqlalchemy.sql import func

from app.db.database import Base


class Competitor(Base):

    __tablename__ = "competitors"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "competitor_name",
            name="uq_competitors_company_name"
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

    competitor_name = Column(
        String,
        nullable=False
    )

    source = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
