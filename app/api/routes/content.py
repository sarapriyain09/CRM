from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.content import (
    ContentApprovedResponse,
    ContentApproveRequest,
    ContentApproveResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
)
from app.services.content import generate_content_packs, list_approved_content_packs, approve_content_pack

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/generate", response_model=ContentGenerateResponse, status_code=201)
def generate(payload: ContentGenerateRequest, db: Session = Depends(get_db)):
    try:
        return generate_content_packs(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/approved", response_model=ContentApprovedResponse)
def approved(limit: int = 50, db: Session = Depends(get_db)):
    return {"packs": list_approved_content_packs(db, limit=limit)}


@router.post("/{content_pack_id}/approve", response_model=ContentApproveResponse)
def approve(content_pack_id: int, payload: ContentApproveRequest, db: Session = Depends(get_db)):
    try:
        pack = approve_content_pack(db, content_pack_id, payload.is_approved)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ContentApproveResponse(content_pack_id=pack.id, is_approved=pack.is_approved)
