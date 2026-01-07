from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PlatformType, PostStatus
from app.schemas.common import ORMBase


class PostScheduleRequest(BaseModel):
    campaign_id: int
    content_pack_id: int | None = None
    platform: PlatformType
    scheduled_at: datetime | None = None


class PostStatusUpdate(BaseModel):
    post_id: int
    status: PostStatus
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    external_post_id: str | None = None
    post_url: str | None = None


class PostMetricsUpdate(BaseModel):
    post_id: int
    metrics: dict = Field(default_factory=dict)


class PostOut(ORMBase):
    id: int
    campaign_id: int
    content_pack_id: int | None
    platform: PlatformType
    status: PostStatus
    scheduled_at: datetime | None
    published_at: datetime | None
    external_post_id: str | None
    post_url: str | None
    metrics: dict
    created_at: datetime


class PostScheduleResponse(BaseModel):
    post_id: int
    status: PostStatus
    scheduled_at: datetime | None


class PostStatusUpdateResponse(BaseModel):
    post_id: int
    status: PostStatus


class PostMetricsResponse(BaseModel):
    post_id: int
    updated: bool


class PostRecentItem(BaseModel):
    post_id: int
    platform: PlatformType
    status: PostStatus
    post_url: str | None = None


class PostRecentResponse(BaseModel):
    items: list[PostRecentItem]
