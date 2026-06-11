from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from sqlalchemy.sql import func

from app.db.database import Base


class JobListing(Base):

    __tablename__ = "job_listings"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "title",
            name="uq_job_listings_company_title"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    location = Column(String)

    job_url = Column(String)

    url = Column(String)

    department = Column(String)

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
