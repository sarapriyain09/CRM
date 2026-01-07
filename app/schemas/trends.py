from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field

from app.schemas.common import ORMBase


class TrendItemIn(BaseModel):
    # Accept MVP spec fields + backward-compatible aliases.
    source: str = Field(min_length=1, validation_alias=AliasChoices("source", "source_name"))
    topic: str = Field(min_length=1)
    url: str | None = None
    category: str | None = None
    language: str | None = None

    metrics: dict = Field(default_factory=dict)
    features: dict = Field(default_factory=dict)


class TrendIngestRequest(BaseModel):
    region: str = Field(min_length=1)
    items: list[TrendItemIn]


class TrendIngestTopTrend(BaseModel):
    trend_item_id: int
    topic: str
    score: float
    region: str
    category: str | None = None
    url: str | None = None


class TrendIngestResponse(BaseModel):
    ingested: int
    top_trends: list[TrendIngestTopTrend]

    # Backward-compat for older n8n workflows / callers.
    ingested_count: int | None = None


class TrendTopItem(BaseModel):
    trend_item_id: int
    topic: str
    score: float
    category: str | None = None
    last_seen_at: datetime
    url: str | None = None


class TrendTopResponse(BaseModel):
    region: str
    items: list[TrendTopItem]


class TrendItemOut(ORMBase):
    id: int
    source_id: int
    region: str
    language: str | None
    topic: str
    url: str | None
    category: str | None
    score: float
    features: dict
    first_seen_at: datetime
    last_seen_at: datetime
