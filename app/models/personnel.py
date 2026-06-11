from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from sqlalchemy.sql import func

from app.db.database import Base


class Personnel(Base):

    __tablename__ = "personnel"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "name",
            name="uq_personnel_company_name"
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

    name = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=True
    )

    title = Column(
        String,
        nullable=True
    )

    linkedin_url = Column(
        String,
        nullable=True
    )

    first_seen = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    status = Column(
        String,
        nullable=False,
        default="active"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
