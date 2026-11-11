import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.db.models.telemetry import APIKey
from app.db.models.user import User


def create_api_key(project: Project, db: Session) -> tuple[APIKey, str]:
    key_id = secrets.token_urlsafe(9)
    prefix = f"efk_{key_id}"
    secret = f"{prefix}.{secrets.token_urlsafe(32)}"
    api_key = APIKey(
        id=uuid4(),
        project_id=project.id,
        key_id=key_id,
        prefix=prefix,
        key_hash=hashlib.sha256(secret.encode("utf-8")).hexdigest(),
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, secret


def list_api_keys(project: Project, db: Session) -> list[APIKey]:
    statement = (
        select(APIKey)
        .where(APIKey.project_id == project.id)
        .order_by(APIKey.created_at.desc(), APIKey.id)
    )
    return list(db.scalars(statement))


def revoke_api_key(key_id: UUID, owner: User, db: Session) -> None:
    api_key = db.scalar(
        select(APIKey)
        .join(Project, APIKey.project_id == Project.id)
        .where(APIKey.id == key_id, Project.owner_user_id == owner.id)
    )
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    if api_key.revoked_at is None:
        api_key.revoked_at = datetime.now(timezone.utc)
        db.commit()


def authenticate_api_key(secret: str, db: Session) -> APIKey | None:
    prefix, separator, _material = secret.partition(".")
    if not separator or not prefix.startswith("efk_"):
        return None
    key_id = prefix[4:]
    if not key_id:
        return None
    api_key = db.scalar(select(APIKey).where(APIKey.key_id == key_id))
    if api_key is None or api_key.revoked_at is not None:
        return None
    supplied_hash = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(supplied_hash, api_key.key_hash):
        return None
    return api_key
