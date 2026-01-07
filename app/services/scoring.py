from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_event import LeadEvent
from app.schemas.scoring import LeadScoreOut


SCORE_RULES: dict[str, int] = {
    "visited_pricing": 10,
    "codlearn_project_created": 20,
    "export_attempt": 30,
    "intent_ecommerce_selected": 40,
    "contact_form_submitted": 50,
}


def calculate_score_for_lead(db: Session, lead_id: int) -> int:
    events = list(db.scalars(select(LeadEvent).where(LeadEvent.lead_id == lead_id)).all())
    score = 0
    for event in events:
        score += SCORE_RULES.get(event.event_type, 0)
    return score


def recalculate_lead_score(db: Session, lead_id: int) -> LeadScoreOut | None:
    lead = db.get(Lead, lead_id)
    if not lead:
        return None

    lead.score = calculate_score_for_lead(db, lead_id)
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return LeadScoreOut(lead_id=lead.id, score=lead.score)
