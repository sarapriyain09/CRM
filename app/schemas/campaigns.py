from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import HandoffTarget
from app.schemas.common import ORMBase


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    region: str = Field(min_length=1)
    target: HandoffTarget = HandoffTarget.codlearn
    offer: str | None = None
    niche: str | None = None
    status: str = "active"


class CampaignCreateResponse(BaseModel):
    campaign_id: int
    name: str
    slug: str
    region: str
    target: HandoffTarget
    status: str


class CampaignListResponse(BaseModel):
    items: list[CampaignCreateResponse]


class CampaignOut(ORMBase):
    id: int
    name: str
    region: str
    target: HandoffTarget
    offer: str | None
    niche: str | None
    status: str
    slug: str | None

    created_at: datetime
    updated_at: datetime
