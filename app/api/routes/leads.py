from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.lead import (
    LeadEventCreate,
    LeadEventCreateResponse,
    LeadListItem,
    LeadListResponse,
    LeadNoteCreate,
    LeadNoteCreateResponse,
    LeadOut,
    LeadTaskCreate,
    LeadTaskCreateResponse,
    LeadUpsert,
    LeadUpsertResponse,
)
from app.services.leads import (
    add_lead_event,
    add_lead_note,
    add_lead_task,
    get_lead,
    list_leads,
    upsert_lead,
)
from app.schemas.scoring import LeadScoreDetailOut
from app.services.scoring import recalculate_lead_score

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upsert", response_model=LeadUpsertResponse)
def upsert(payload: LeadUpsert, db: Session = Depends(get_db)):
    lead, created = upsert_lead(db, payload)
    return {"lead_id": lead.id, "created": created}


@router.get("/", response_model=LeadListResponse)
def list_all(
    status: str | None = None,
    intent: str | None = None,
    min_score: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    leads = list_leads(db, status=status, intent=intent, min_score=min_score, limit=limit)
    items = [
        LeadListItem(
            lead_id=l.id,
            email=l.email,
            status=l.status,
            score=l.score,
            intent=l.intent,
        )
        for l in leads
    ]
    return LeadListResponse(items=items)


@router.get("/{lead_id}", response_model=LeadOut)
def get_one(lead_id: int, db: Session = Depends(get_db)):
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/events", response_model=LeadEventCreateResponse, status_code=201)
def add_event(lead_id: int, payload: LeadEventCreate, db: Session = Depends(get_db)):
    try:
        event = add_lead_event(db, lead_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"event_id": event.id}


@router.post("/{lead_id}/notes", response_model=LeadNoteCreateResponse, status_code=201)
def add_note(lead_id: int, payload: LeadNoteCreate, db: Session = Depends(get_db)):
    try:
        note = add_lead_note(db, lead_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"note_id": note.id}


@router.post("/{lead_id}/tasks", response_model=LeadTaskCreateResponse, status_code=201)
def add_task(lead_id: int, payload: LeadTaskCreate, db: Session = Depends(get_db)):
    try:
        task = add_lead_task(db, lead_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"task_id": task.id}


@router.post("/{lead_id}/score/recalculate", response_model=LeadScoreDetailOut)
def recalc_score(lead_id: int, db: Session = Depends(get_db)):
    score_out = recalculate_lead_score(db, lead_id)
    if not score_out:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadScoreDetailOut(lead_id=lead_id, score=score_out.score, status=lead.status, intent=lead.intent)
