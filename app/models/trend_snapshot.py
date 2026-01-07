from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trend_item_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("trend_items.id", ondelete="CASCADE"), nullable=False)

    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    trend_item = relationship("TrendItem")
