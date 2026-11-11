import json
from datetime import datetime, timezone
from typing import Any, NamedTuple, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.telemetry import Event, Span, Trace
from app.schemas.telemetry import EventInput, IngestBatch, SpanInput, TraceInput

class IngestBatchLimits(NamedTuple):
    max_records: int
    max_bytes: int


INGEST_BATCH_LIMITS = IngestBatchLimits(max_records=100, max_bytes=1_000_000)

_T = TypeVar("_T", TraceInput, SpanInput, EventInput)
_MODEL_BY_TYPE = {
    TraceInput: Trace,
    SpanInput: Span,
    EventInput: Event,
}
_COST_FIELDS = {"estimated_cost", "estimated_cost_currency"}


def ingest_batch(batch: IngestBatch, project_id: UUID, db: Session) -> dict[str, Any]:
    if batch.project_id is not None and batch.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="project_id must match the authenticated API key project",
        )
    record_count = len(batch.traces) + len(batch.spans) + len(batch.events)
    if record_count > INGEST_BATCH_LIMITS.max_records:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Batch exceeds the record limit",
        )

    try:
        if batch.schema_version != "1":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Unsupported schema_version",
            )

        duplicates = {"traces": 0, "spans": 0, "events": 0}
        inserted: dict[str, int] = {}
        records: dict[type[Any], dict[UUID, Any]] = {}
        database_records: dict[type[Any], dict[UUID, Any]] = {}

        for input_type, model, attribute, counter_name in (
            (TraceInput, Trace, batch.traces, "traces"),
            (SpanInput, Span, batch.spans, "spans"),
            (EventInput, Event, batch.events, "events"),
        ):
            by_id = _deduplicate_batch_records(
                attribute,
                input_type,
                duplicates,
                counter_name,
            )
            records[input_type] = by_id
            found = (
                list(db.scalars(select(model).where(model.id.in_(by_id))))
                if by_id
                else []
            )
            database_records[input_type] = {record.id: record for record in found}
            new_records: dict[UUID, Any] = {}
            for record_id, record in by_id.items():
                existing = database_records[input_type].get(record_id)
                if existing is None:
                    new_records[record_id] = record
                    continue
                if (
                    existing.project_id != project_id
                    or _canonical_input(record) != _canonical_database(existing, input_type)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A record ID already exists with different canonical content",
                    )
                duplicates[counter_name] += 1
            records[input_type] = new_records
            inserted[counter_name] = len(new_records)

        _validate_trace_references(
            project_id,
            records,
            batch,
            db,
        )
        _validate_span_relationships(project_id, records, database_records, db)
        _validate_event_relationships(project_id, records, db)

        for input_type in (TraceInput, SpanInput, EventInput):
            model = _MODEL_BY_TYPE[input_type]
            for record in records[input_type].values():
                values = record.model_dump(exclude=_COST_FIELDS)
                db.add(model(project_id=project_id, **values))
            db.flush()

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A record conflicts with persisted telemetry",
        ) from None
    except Exception:
        db.rollback()
        raise

    return {
        "batch_id": batch.batch_id,
        "inserted": inserted,
        "duplicates": duplicates,
    }


def _deduplicate_batch_records(
    payloads: list[_T],
    input_type: type[_T],
    duplicates: dict[str, int],
    counter_name: str,
) -> dict[UUID, _T]:
    unique: dict[UUID, _T] = {}
    for payload in payloads:
        previous = unique.get(payload.id)
        if previous is None:
            unique[payload.id] = payload
        elif _canonical_input(previous) == _canonical_input(payload):
            duplicates[counter_name] += 1
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record ID is repeated with different canonical content",
            )
    return unique


def _canonical_input(record: Any) -> str:
    values = record.model_dump(mode="json", exclude=_COST_FIELDS)
    return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _canonical_database(record: Any, input_type: type[Any]) -> str:
    fields = input_type.model_fields.keys() - _COST_FIELDS
    values = {field: getattr(record, field) for field in fields}
    normalized = {key: _json_value(value) for key, value in values.items()}
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _json_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _validate_trace_references(
    project_id: UUID,
    records: dict[type[Any], dict[UUID, Any]],
    batch: IngestBatch,
    db: Session,
) -> None:
    referencing_trace_ids = {span.trace_id for span in batch.spans}
    referencing_trace_ids.update(event.trace_id for event in batch.events)
    if not referencing_trace_ids:
        return
    incoming_trace_ids = set(records[TraceInput])
    found = set(
        db.scalars(
            select(Trace.id).where(
                Trace.project_id == project_id,
                Trace.id.in_(referencing_trace_ids - incoming_trace_ids),
            )
        )
    )
    if not referencing_trace_ids.issubset(incoming_trace_ids | found):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Every span and event must reference a trace in this project",
        )


def _validate_span_relationships(
    project_id: UUID,
    records: dict[type[Any], dict[UUID, Any]],
    database_records: dict[type[Any], dict[UUID, Any]],
    db: Session,
) -> None:
    incoming_spans: dict[UUID, SpanInput] = records[SpanInput]
    candidate_parents = {
        span.parent_span_id
        for span in incoming_spans.values()
        if span.parent_span_id is not None
    }
    found_parent_spans = {
        span.id: span
        for span in db.scalars(
            select(Span).where(
                Span.project_id == project_id,
                Span.id.in_(candidate_parents - incoming_spans.keys()),
            )
        )
    }
    existing_same_ids = database_records[SpanInput]
    parents: dict[UUID, UUID | None] = {}
    known_span_trace: dict[UUID, UUID] = {
        span_id: span.trace_id for span_id, span in incoming_spans.items()
    }
    known_span_trace.update(
        {span_id: span.trace_id for span_id, span in existing_same_ids.items()}
    )
    known_span_trace.update(
        {span_id: span.trace_id for span_id, span in found_parent_spans.items()}
    )
    for span in incoming_spans.values():
        parent_id = span.parent_span_id
        parents[span.id] = parent_id
        if parent_id is None:
            continue
        parent_trace_id = known_span_trace.get(parent_id)
        if parent_trace_id != span.trace_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="A parent span must belong to the same trace",
            )

    for span_id in incoming_spans:
        visited: set[UUID] = set()
        current: UUID | None = span_id
        while current is not None and current in parents:
            if current in visited:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Span parent relationships must not contain cycles",
                )
            visited.add(current)
            parent_id = parents[current]
            if parent_id in found_parent_spans:
                parent = found_parent_spans[parent_id]
                parents[parent.id] = parent.parent_span_id
            current = parent_id


def _validate_event_relationships(
    project_id: UUID,
    records: dict[type[Any], dict[UUID, Any]],
    db: Session,
) -> None:
    events: dict[UUID, EventInput] = records[EventInput]
    span_ids = {event.span_id for event in events.values() if event.span_id is not None}
    if not span_ids:
        return
    new_spans: dict[UUID, SpanInput] = records[SpanInput]
    found_spans = {
        span.id: span
        for span in db.scalars(
            select(Span).where(Span.project_id == project_id, Span.id.in_(span_ids))
        )
    }
    for event in events.values():
        if event.span_id is None:
            continue
        span = new_spans.get(event.span_id) or found_spans.get(event.span_id)
        if span is None or span.trace_id != event.trace_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="An event span must belong to the event trace",
            )
