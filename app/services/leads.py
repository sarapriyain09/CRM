from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.handoff_request import HandoffRequest
from app.models.lead import Lead
from app.models.lead_event import LeadEvent
from app.models.lead_note import LeadNote
from app.models.lead_task import LeadTask
from app.models.scoring_rule import ScoringRule
from app.models.enums import HandoffTarget
from app.schemas.lead import LeadEventCreate, LeadNoteCreate, LeadTaskCreate, LeadUpsert


SALES_READY_THRESHOLD = 60


def upsert_lead(db: Session, payload: LeadUpsert) -> tuple[Lead, bool]:
    data = payload.model_dump()
    email = data.get("email")

    if email:
        existing = db.scalar(select(Lead).where(Lead.email == email))
        if existing:
            for key, value in data.items():
                if value is not None:
                    setattr(existing, key, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing, False

    lead = Lead(**data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead, True


def list_leads(
    db: Session,
    status: str | None = None,
    intent: str | None = None,
    min_score: int | None = None,
    limit: int = 50,
) -> list[Lead]:
    stmt = select(Lead).order_by(Lead.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(Lead.status == status)
    if intent:
        stmt = stmt.where(Lead.intent == intent)
    if min_score is not None:
        stmt = stmt.where(Lead.score >= int(min_score))
    return list(db.scalars(stmt).all())


def get_lead(db: Session, lead_id: int) -> Lead | None:
    return db.get(Lead, lead_id)


def add_lead_event(db: Session, lead_id: int, payload: LeadEventCreate) -> LeadEvent:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise ValueError("Lead not found")

    data = payload.model_dump()
    event_at = data.get("event_at")
    if event_at is not None and event_at.tzinfo is None:
        data["event_at"] = event_at.replace(tzinfo=timezone.utc)

    event = LeadEvent(
        lead_id=lead_id,
        event_type=data["event_type"],
        event_at=data.get("event_at"),
        meta=data.get("metadata", {}),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    _recalculate_score_and_handoff(db, lead_id)
    return event


def add_lead_note(db: Session, lead_id: int, payload: LeadNoteCreate) -> LeadNote:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise ValueError("Lead not found")

    note = LeadNote(lead_id=lead_id, note=payload.note)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def add_lead_task(db: Session, lead_id: int, payload: LeadTaskCreate) -> LeadTask:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise ValueError("Lead not found")

    task = LeadTask(lead_id=lead_id, title=payload.title, due_at=payload.due_at)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _recalculate_score_and_handoff(db: Session, lead_id: int) -> None:
    lead = db.get(Lead, lead_id)
    if not lead:
        return

    rules = {r.code: r for r in db.scalars(select(ScoringRule).where(ScoringRule.enabled.is_(True))).all()}
    events = list(db.scalars(select(LeadEvent).where(LeadEvent.lead_id == lead_id)).all())

    score = 0
    for event in events:
        rule = rules.get(event.event_type)
        if rule:
            score += int(rule.points)

    lead.score = score
    db.add(lead)
    db.commit()
    db.refresh(lead)

    if lead.score >= SALES_READY_THRESHOLD:
        # Idempotency: don't spam handoffs; keep one handoff per lead for now.
        existing = db.scalar(select(HandoffRequest).where(HandoffRequest.lead_id == lead_id))
        if not existing:
            db.add(
                HandoffRequest(
                    lead_id=lead_id,
                    target=HandoffTarget.splendid,
                    reason=f"score>={SALES_READY_THRESHOLD}",
                    payload={},
                )
            )
            db.commit()
