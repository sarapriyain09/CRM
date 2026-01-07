from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PlatformType


class ContentPack(Base):
    __tablename__ = "content_packs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    campaign_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    trend_item_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("trend_items.id", ondelete="SET NULL"), nullable=True)

    platform: Mapped[PlatformType] = mapped_column(Enum(PlatformType, name="platform_type"), nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)

    content_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    quality_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    campaign = relationship("Campaign")
