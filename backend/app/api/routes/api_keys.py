from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.schemas.api_key import APIKeyCreated, APIKeyMetadata
from app.services.api_keys import create_api_key, list_api_keys, revoke_api_key
from app.services.projects import get_owned_project

router = APIRouter(tags=["api keys"])


@router.post(
    "/projects/{project_id}/api-keys",
    response_model=APIKeyCreated,
    status_code=status.HTTP_201_CREATED,
)
def create(
    project_id: UUID,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> APIKeyCreated:
    project = get_owned_project(project_id, owner, db)
    api_key, secret = create_api_key(project, db)
    return APIKeyCreated(
        id=api_key.id,
        key_id=api_key.key_id,
        prefix=api_key.prefix,
        secret=secret,
        created_at=api_key.created_at,
    )


@router.get(
    "/projects/{project_id}/api-keys",
    response_model=list[APIKeyMetadata],
)
def list_owned(
    project_id: UUID,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[APIKeyMetadata]:
    project = get_owned_project(project_id, owner, db)
    return list_api_keys(project, db)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    key_id: UUID,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    revoke_api_key(key_id, owner, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
