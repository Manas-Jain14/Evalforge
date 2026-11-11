from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CanonicalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("attributes", check_fields=False)
    @classmethod
    def reject_prompt_payloads(cls, value: dict[str, Any]) -> dict[str, Any]:
        forbidden = {"prompt", "prompts", "completion", "completions"}
        pending: list[Any] = [value]
        while pending:
            current = pending.pop()
            if isinstance(current, dict):
                if any(key.lower() in forbidden for key in current if isinstance(key, str)):
                    raise ValueError("Prompt and completion payloads are not accepted")
                pending.extend(current.values())
            elif isinstance(current, list):
                pending.extend(current)
        return value

    @field_validator("*", mode="after")
    @classmethod
    def normalize_timestamps(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("Timestamps must include a timezone")
            return value.astimezone(timezone.utc)
        return value

    @model_validator(mode="after")
    def validate_time_order(self) -> "CanonicalRecord":
        if hasattr(self, "start_time") and self.end_time < self.start_time:
            raise ValueError("end_time must not be before start_time")
        return self


class TraceInput(CanonicalRecord):
    id: UUID
    external_id: str | None = Field(default=None, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    status: str = Field(min_length=1, max_length=32)
    start_time: datetime
    end_time: datetime
    duration_ms: int = Field(ge=0)
    environment: str | None = Field(default=None, max_length=128)
    service_name: str | None = Field(default=None, max_length=128)
    attributes: dict[str, Any] = Field(default_factory=dict)


class SpanInput(CanonicalRecord):
    id: UUID
    trace_id: UUID
    parent_span_id: UUID | None = None
    name: str = Field(min_length=1, max_length=255)
    operation_type: str = Field(min_length=1, max_length=64)
    status: str = Field(min_length=1, max_length=32)
    start_time: datetime
    end_time: datetime
    duration_ms: int = Field(ge=0)
    provider: str | None = Field(default=None, max_length=128)
    model: str | None = Field(default=None, max_length=255)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    estimated_cost: Any = None
    estimated_cost_currency: Any = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    error_type: str | None = Field(default=None, max_length=255)
    error_message: str | None = None


class EventInput(CanonicalRecord):
    id: UUID
    trace_id: UUID
    span_id: UUID | None = None
    event_type: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    timestamp: datetime
    message: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class IngestBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"]
    batch_id: str | None = Field(default=None, max_length=128)
    project_id: UUID | None = None
    traces: list[TraceInput] = Field(default_factory=list)
    spans: list[SpanInput] = Field(default_factory=list)
    events: list[EventInput] = Field(default_factory=list)


class TraceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    external_id: str | None
    name: str
    status: str
    start_time: datetime
    end_time: datetime
    duration_ms: int
    environment: str | None
    service_name: str | None
    attributes: dict[str, Any]
    created_at: datetime


class SpanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    trace_id: UUID
    parent_span_id: UUID | None
    name: str
    operation_type: str
    status: str
    start_time: datetime
    end_time: datetime
    duration_ms: int
    provider: str | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost: None
    estimated_cost_currency: None
    attributes: dict[str, Any]
    error_type: str | None
    error_message: str | None
    created_at: datetime


class SpanNode(SpanResponse):
    children: list["SpanNode"] = Field(default_factory=list)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    trace_id: UUID
    span_id: UUID | None
    event_type: str
    name: str
    timestamp: datetime
    message: str | None
    attributes: dict[str, Any]
    created_at: datetime


class TraceDetail(BaseModel):
    trace: TraceResponse
    spans: list[SpanNode]
    events: list[EventResponse]
