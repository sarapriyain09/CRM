from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field

from app.models.enums import PlatformType
from app.schemas.common import ORMBase


class ContentGenerateRequest(BaseModel):
    # Prefer slug (matches n8n + UTMs); accept legacy campaign_id too.
    campaign_slug: str | None = Field(default=None, validation_alias=AliasChoices("campaign_slug", "campaignSlug"))
    campaign_id: int | None = None
    trend_item_id: int | None = None
    platforms: list[PlatformType] = Field(min_length=1)

    # Optional: if n8n/LLM already generated content, pass it through.
    content_json_by_platform: dict[str, dict] = Field(default_factory=dict)

    # Spec fields (stored into content_json when provided)
    cta: dict[str, str] = Field(default_factory=dict)
    target: str = "codlearn"


class ContentPackOut(ORMBase):
    id: int
    campaign_id: int
    trend_item_id: int | None
    platform: PlatformType
    title: str | None
    content_json: dict
    quality_score: float
    is_approved: bool
    created_at: datetime


class ContentGenerateResponse(BaseModel):
    campaign_slug: str
    created: int
    packs: list[dict]


class ContentApprovedResponse(BaseModel):
    packs: list[ContentPackOut]


class ContentApproveRequest(BaseModel):
    is_approved: bool


class ContentApproveResponse(BaseModel):
    content_pack_id: int
    is_approved: bool
