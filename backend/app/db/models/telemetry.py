from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    JSON,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_JSON_OBJECT = JSON().with_variant(JSONB, "postgresql")


class APIKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        UniqueConstraint("key_id", name="uq_api_keys_key_id"),
        UniqueConstraint("key_hash", name="uq_api_keys_key_hash"),
        Index("ix_api_keys_project_id_created_at", "project_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    key_id: Mapped[str] = mapped_column(String(32), nullable=False)
    prefix: Mapped[str] = mapped_column(String(24), nullable=False)
    key_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Trace(Base):
    __tablename__ = "traces"
    __table_args__ = (
        UniqueConstraint("project_id", "id", name="uq_traces_project_id_id"),
        CheckConstraint("duration_ms >= 0", name="ck_traces_duration_nonnegative"),
        Index("ix_traces_project_id_start_time", "project_id", "start_time"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    environment: Mapped[str | None] = mapped_column(String(128))
    service_name: Mapped[str | None] = mapped_column(String(128))
    attributes: Mapped[dict[str, Any]] = mapped_column(_JSON_OBJECT, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Span(Base):
    __tablename__ = "spans"
    __table_args__ = (
        UniqueConstraint("project_id", "trace_id", "id", name="uq_spans_project_trace_id_id"),
        ForeignKeyConstraint(
            ["project_id", "trace_id"],
            ["traces.project_id", "traces.id"],
            name="fk_spans_project_trace",
        ),
        ForeignKeyConstraint(
            ["project_id", "trace_id", "parent_span_id"],
            ["spans.project_id", "spans.trace_id", "spans.id"],
            name="fk_spans_parent_same_trace",
        ),
        CheckConstraint("duration_ms >= 0", name="ck_spans_duration_nonnegative"),
        CheckConstraint("input_tokens IS NULL OR input_tokens >= 0", name="ck_spans_input_tokens_nonnegative"),
        CheckConstraint("output_tokens IS NULL OR output_tokens >= 0", name="ck_spans_output_tokens_nonnegative"),
        CheckConstraint("total_tokens IS NULL OR total_tokens >= 0", name="ck_spans_total_tokens_nonnegative"),
        CheckConstraint("estimated_cost IS NULL OR estimated_cost >= 0", name="ck_spans_estimated_cost_nonnegative"),
        CheckConstraint(
            "(estimated_cost IS NULL AND estimated_cost_currency IS NULL) OR "
            "(estimated_cost IS NOT NULL AND estimated_cost_currency IS NOT NULL)",
            name="ck_spans_cost_currency_pair",
        ),
        CheckConstraint("parent_span_id IS NULL OR parent_span_id != id", name="ck_spans_not_self_parent"),
        Index("ix_spans_project_id_trace_id", "project_id", "trace_id"),
        Index("ix_spans_project_id_parent_span_id", "project_id", "parent_span_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    trace_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    parent_span_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(128))
    model: Mapped[str | None] = mapped_column(String(255))
    input_tokens: Mapped[int | None] = mapped_column(BigInteger)
    output_tokens: Mapped[int | None] = mapped_column(BigInteger)
    total_tokens: Mapped[int | None] = mapped_column(BigInteger)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(20, 10))
    estimated_cost_currency: Mapped[str | None] = mapped_column(String(3))
    attributes: Mapped[dict[str, Any]] = mapped_column(_JSON_OBJECT, nullable=False, default=dict)
    error_type: Mapped[str | None] = mapped_column(String(255))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "trace_id"],
            ["traces.project_id", "traces.id"],
            name="fk_events_project_trace",
        ),
        ForeignKeyConstraint(
            ["project_id", "trace_id", "span_id"],
            ["spans.project_id", "spans.trace_id", "spans.id"],
            name="fk_events_span_same_trace",
        ),
        Index("ix_events_project_id_timestamp", "project_id", "timestamp"),
        Index("ix_events_project_id_trace_id_timestamp", "project_id", "trace_id", "timestamp"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    trace_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    span_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    attributes: Mapped[dict[str, Any]] = mapped_column(_JSON_OBJECT, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
