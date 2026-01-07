from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import LeadIntent, LeadStatus, PlatformType
from app.schemas.common import ORMBase


class LeadUpsert(BaseModel):
    # Upsert key: email (preferred). If missing, we will create a new lead.
    email: EmailStr | None = None

    phone: str | None = None
    full_name: str | None = None
    company: str | None = None
    region: str | None = None

    source_platform: PlatformType = PlatformType.other
    source_detail: str | None = None

    intent: LeadIntent = LeadIntent.unknown
    status: LeadStatus = LeadStatus.new

    attributes: dict = Field(default_factory=dict)


class LeadOut(ORMBase):
    id: int
    email: str | None
    phone: str | None
    full_name: str | None
    company: str | None
    region: str | None

    source_platform: PlatformType
    source_detail: str | None

    intent: LeadIntent
    status: LeadStatus
    score: int
    attributes: dict

    created_at: datetime
    updated_at: datetime


class LeadUpsertResponse(BaseModel):
    lead_id: int
    created: bool


class LeadListItem(BaseModel):
    lead_id: int
    email: str | None = None
    status: LeadStatus
    score: int
    intent: LeadIntent


class LeadListResponse(BaseModel):
    items: list[LeadListItem]


class LeadEventCreate(BaseModel):
    event_type: str = Field(min_length=1)
    event_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)


class LeadEventOut(ORMBase):
    id: int
    lead_id: int
    event_type: str
    event_at: datetime
    metadata: dict


class LeadNoteCreate(BaseModel):
    note: str = Field(min_length=1)


class LeadNoteOut(ORMBase):
    id: int
    lead_id: int
    note: str
    created_at: datetime


class LeadTaskCreate(BaseModel):
    title: str = Field(min_length=1)
    due_at: datetime | None = None


class LeadTaskOut(ORMBase):
    id: int
    lead_id: int
    title: str
    due_at: datetime | None
    is_done: bool
    created_at: datetime


class LeadEventCreateResponse(BaseModel):
    event_id: int


class LeadNoteCreateResponse(BaseModel):
    note_id: int


class LeadTaskCreateResponse(BaseModel):
    task_id: int
