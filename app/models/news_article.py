from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from sqlalchemy.sql import func

from app.db.database import Base


class NewsArticle(Base):

    __tablename__ = "news_articles"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "title",
            name="uq_news_articles_company_title"
        ),
        UniqueConstraint(
            "company_id",
            "url",
            name="uq_news_articles_company_url"
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

    title = Column(
        String,
        nullable=False
    )

    url = Column(
        String,
        nullable=False
    )

    published_at = Column(
        String,
        nullable=True
    )

    source_type = Column(
        String,
        nullable=False,
        default="NEWS"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
