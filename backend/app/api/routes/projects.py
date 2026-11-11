from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.db.models.project import Project
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.projects import (
    create_project,
    get_owned_project,
    list_projects,
    update_project,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: ProjectCreate,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    return create_project(payload, owner, db)


@router.get("", response_model=list[ProjectResponse])
def list_owned(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Project]:
    return list_projects(owner, db, offset=offset, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_one(
    project_id: UUID,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    return get_owned_project(project_id, owner, db)


@router.patch("/{project_id}", response_model=ProjectResponse)
def patch(
    project_id: UUID,
    payload: ProjectUpdate,
    owner: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    return update_project(project_id, payload, owner, db)
