from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import HandoffTarget


class HandoffRequest(Base):
    __tablename__ = "handoff_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)

    target: Mapped[HandoffTarget] = mapped_column(
        Enum(HandoffTarget, name="handoff_target"),
        nullable=False,
        default=HandoffTarget.splendid,
    )
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    lead = relationship("Lead")
