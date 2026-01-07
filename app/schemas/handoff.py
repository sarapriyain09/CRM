from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import HandoffTarget
from app.schemas.common import ORMBase


class HandoffRequestCreate(BaseModel):
    lead_id: int
    target: HandoffTarget = HandoffTarget.splendid
    reason: str | None = None
    payload: dict = Field(default_factory=dict)


class HandoffRequestOut(ORMBase):
    id: int
    lead_id: int
    target: HandoffTarget
    reason: str | None
    payload: dict
    created_at: datetime


class HandoffCreateResponse(BaseModel):
    handoff_id: int


class HandoffRecentItem(BaseModel):
    handoff_id: int
    lead_id: int
    target: HandoffTarget
    created_at: datetime


class HandoffRecentResponse(BaseModel):
    items: list[HandoffRecentItem]
