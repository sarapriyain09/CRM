from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.handoff_request import HandoffRequest
from app.schemas.handoff import HandoffRequestCreate


def create_handoff(db: Session, payload: HandoffRequestCreate) -> HandoffRequest:
    req = HandoffRequest(**payload.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def list_recent_handoffs(db: Session, limit: int = 50) -> list[HandoffRequest]:
    stmt = select(HandoffRequest).order_by(HandoffRequest.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())
