from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIKeyMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key_id: str
    prefix: str
    created_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None


class APIKeyCreated(BaseModel):
    id: UUID
    key_id: str
    prefix: str
    secret: str
    created_at: datetime


class IngestCounts(BaseModel):
    traces: int
    spans: int
    events: int


class IngestBatchResponse(BaseModel):
    batch_id: str | None
    inserted: IngestCounts
    duplicates: IngestCounts
