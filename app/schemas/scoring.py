from pydantic import BaseModel

from app.models.enums import LeadIntent, LeadStatus


class LeadScoreOut(BaseModel):
    lead_id: int
    score: int


class LeadScoreDetailOut(BaseModel):
    lead_id: int
    score: int
    status: LeadStatus
    intent: LeadIntent


class ScoreRulesOut(BaseModel):
    rules: dict[str, int]
