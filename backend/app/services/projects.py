from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(payload: ProjectCreate, owner: User, db: Session) -> Project:
    project = Project(
        owner_user_id=owner.id,
        name=payload.name,
        description=payload.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(owner: User, db: Session, *, offset: int, limit: int) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.owner_user_id == owner.id)
        .order_by(Project.created_at.desc(), Project.id)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement))


def get_owned_project(project_id: UUID, owner: User, db: Session) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_user_id == owner.id,
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    owner: User,
    db: Session,
) -> Project:
    project = get_owned_project(project_id, owner, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project
