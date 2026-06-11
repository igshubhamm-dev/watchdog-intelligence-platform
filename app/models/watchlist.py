from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.db.database import Base


class Watchlist(Base):

    __tablename__ = "watchlists"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_name = Column(
        String,
        nullable=False
    )

    website = Column(
        String,
        nullable=False,
        unique=True
    )