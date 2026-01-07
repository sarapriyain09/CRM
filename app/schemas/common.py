from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Timestamped(BaseModel):
    created_at: datetime


class UUIDModel(BaseModel):
    id: UUID
