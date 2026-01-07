from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.handoff import (
    HandoffCreateResponse,
    HandoffRecentItem,
    HandoffRecentResponse,
    HandoffRequestCreate,
)
from app.services.handoff import create_handoff, list_recent_handoffs

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create", response_model=HandoffCreateResponse, status_code=201)
def create(payload: HandoffRequestCreate, db: Session = Depends(get_db)):
    try:
        req = create_handoff(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"handoff_id": req.id}


@router.get("/recent", response_model=HandoffRecentResponse)
def recent(limit: int = 50, db: Session = Depends(get_db)):
    reqs = list_recent_handoffs(db, limit=limit)
    items = [HandoffRecentItem(handoff_id=r.id, lead_id=r.lead_id, target=r.target, created_at=r.created_at) for r in reqs]
    return HandoffRecentResponse(items=items)
