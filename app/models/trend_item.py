from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrendItem(Base):
    __tablename__ = "trend_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("trend_sources.id", ondelete="RESTRICT"), nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)

    score: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False, default=0)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    source = relationship("TrendSource")
