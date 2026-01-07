from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.scoring import LeadScoreOut, ScoreRulesOut
from app.services.scoring import (
    recalculate_lead_score,
    SCORE_RULES,
)

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/rules", response_model=ScoreRulesOut)
def rules() -> ScoreRulesOut:
    return ScoreRulesOut(rules=SCORE_RULES)


@router.post("/leads/{lead_id}/recalculate", response_model=LeadScoreOut)
def recalc(lead_id: int, db: Session = Depends(get_db)) -> LeadScoreOut:
    result = recalculate_lead_score(db, lead_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result
