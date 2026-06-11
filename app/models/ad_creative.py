from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class AdCreative(Base):
    __tablename__ = "ad_creatives"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "platform",
            "ad_text",
            name="uq_ad_creatives_company_platform_text",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    platform = Column(String, nullable=False)
    ad_text = Column(String, nullable=False)
    image_url_desc = Column(String, nullable=True)
    started_at = Column(String, nullable=True)
    ended_at = Column(String, nullable=True)
    spend_range = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
