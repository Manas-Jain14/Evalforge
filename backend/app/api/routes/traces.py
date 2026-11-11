from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.db.models.telemetry import Event, Span, Trace
from app.db.models.user import User
from app.schemas.telemetry import SpanNode, TraceDetail, TraceResponse
from app.services.projects import get_owned_project

router = APIRouter(prefix="/projects", tags=["traces"])


@router.get("/{project_id}/traces", response_model=list[TraceResponse])
def list_traces(
    project_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Trace]:
    project = get_owned_project(project_id, owner, db)
    statement = (
        select(Trace)
        .where(Trace.project_id == project.id)
        .order_by(Trace.start_time.desc(), Trace.id)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement))


@router.get("/{project_id}/traces/{trace_id}", response_model=TraceDetail)
def get_trace(
    project_id: UUID,
    trace_id: UUID,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TraceDetail:
    project = get_owned_project(project_id, owner, db)
    trace = db.scalar(
        select(Trace).where(Trace.id == trace_id, Trace.project_id == project.id)
    )
    if trace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")

    spans = list(
        db.scalars(
            select(Span)
            .where(Span.project_id == project.id, Span.trace_id == trace.id)
            .order_by(Span.start_time, Span.id)
        )
    )
    nodes = {span.id: SpanNode.model_validate(span) for span in spans}
    roots: list[SpanNode] = []
    for span in spans:
        node = nodes[span.id]
        if span.parent_span_id is None:
            roots.append(node)
        else:
            parent = nodes.get(span.parent_span_id)
            if parent is None:
                raise RuntimeError("Stored span has a missing parent")
            parent.children.append(node)

    events = list(
        db.scalars(
            select(Event)
            .where(Event.project_id == project.id, Event.trace_id == trace.id)
            .order_by(Event.timestamp, Event.id)
        )
    )
    return TraceDetail(trace=trace, spans=roots, events=events)
