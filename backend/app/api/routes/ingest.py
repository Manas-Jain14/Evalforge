import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.dependencies import get_api_key, get_db
from app.db.models.telemetry import APIKey
from app.schemas.api_key import IngestBatchResponse
from app.schemas.telemetry import IngestBatch
from app.services.ingestion import INGEST_BATCH_LIMITS, ingest_batch

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/batch", response_model=IngestBatchResponse)
async def ingest(
    request: Request,
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db),
) -> dict:
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > INGEST_BATCH_LIMITS.max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Batch exceeds the request size limit",
            )
        body.extend(chunk)
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Request body must be valid UTF-8 JSON",
        ) from None
    if isinstance(payload, dict):
        record_count = sum(
            len(payload.get(field, []))
            for field in ("traces", "spans", "events")
            if isinstance(payload.get(field, []), list)
        )
        if record_count > INGEST_BATCH_LIMITS.max_records:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Batch exceeds the record limit",
            )
    try:
        batch = IngestBatch.model_validate(payload)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from None

    return ingest_batch(batch, api_key.project_id, db)
