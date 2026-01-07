from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PlatformType, PostStatus


class SocialPost(Base):
    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    campaign_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    content_pack_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("content_packs.id", ondelete="SET NULL"), nullable=True)

    platform: Mapped[PlatformType] = mapped_column(Enum(PlatformType, name="platform_type"), nullable=False)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus, name="post_status"), nullable=False, default=PostStatus.draft)

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    external_post_id: Mapped[str | None] = mapped_column(String, nullable=True)
    post_url: Mapped[str | None] = mapped_column(String, nullable=True)

    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    campaign = relationship("Campaign")
    content_pack = relationship("ContentPack")
