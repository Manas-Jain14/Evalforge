from uuid import uuid4

import pytest
from alembic.script import ScriptDirectory
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Project, User


def test_user_project_foreign_key_and_unique_constraints(db_engine):
    with Session(db_engine) as session:
        user = User(email="owner@example.com", password_hash="not-a-real-hash")
        session.add(user)
        session.commit()

        session.add(
            Project(
                owner_user_id=user.id,
                name="First",
            )
        )
        session.commit()

        session.add(
            User(email="owner@example.com", password_hash="another-hash")
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        session.add(Project(owner_user_id=uuid4(), name="Orphan"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_user_deletion_does_not_cascade_projects(db_engine):
    with Session(db_engine) as session:
        user = User(email="retained@example.com", password_hash="not-a-real-hash")
        session.add(user)
        session.flush()
        session.add(Project(owner_user_id=user.id, name="Retained"))
        session.commit()

        session.delete(user)
        with pytest.raises(IntegrityError):
            session.commit()


def test_alembic_revision_chain_includes_phase_two_without_running_it():
    script = ScriptDirectory("alembic")
    initial = script.get_revision("0001_users_projects")
    head = script.get_revision("head")

    assert initial is not None
    assert initial.down_revision is None
    assert head is not None
    assert head.revision == "0002_api_keys_telemetry"
    assert head.down_revision == "0001_users_projects"


def test_database_dependency_closes_sessions_after_request(db_engine, monkeypatch):
    from app.core.dependencies import get_db

    class TrackingSession(Session):
        closed = False

        def close(self):
            self.closed = True
            super().close()

    factory = sessionmaker(bind=db_engine, class_=TrackingSession)
    monkeypatch.setattr("app.core.dependencies.get_session_factory", lambda: factory)
    generator = get_db()
    session = next(generator)
    assert not session.closed
    generator.close()
    assert session.closed
