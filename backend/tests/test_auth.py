from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.auth import is_duplicate_email_error, register_user


def register(client, email="dev@example.com", password="correct-horse-battery"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )


def login(client, email="dev@example.com", password="correct-horse-battery"):
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


def test_register_hashes_password_and_returns_safe_user(client):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "dev@example.com"
    assert "password" not in body
    assert "password_hash" not in body

    from app.core.dependencies import get_db

    session_generator = client.app.dependency_overrides[get_db]()
    session = next(session_generator)
    try:
        user = session.query(User).filter_by(email="dev@example.com").one()
        assert user.password_hash != "correct-horse-battery"
        assert user.password_hash.startswith("$argon2")
    finally:
        session_generator.close()


def test_duplicate_registration_is_conflict_even_with_email_case_difference(client):
    assert register(client).status_code == 201
    response = register(client, email="DEV@EXAMPLE.COM")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_register_validates_password_length_and_unknown_fields(client):
    short = register(client, password="short")
    assert short.status_code == 422
    assert short.json()["error"]["code"] == "validation_error"

    extra = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "correct-horse-battery",
            "is_admin": True,
        },
    )
    assert extra.status_code == 422


def test_login_returns_bearer_token_and_me_returns_current_user(client):
    register(client)
    response = login(client)

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == 1800

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "dev@example.com"
    assert "password_hash" not in me.json()


def test_login_does_not_disclose_which_credential_was_wrong(client):
    register(client)
    unknown_user = login(client, email="missing@example.com", password="incorrect-password")
    wrong_password = login(client, password="incorrect-password")

    assert unknown_user.status_code == wrong_password.status_code == 401
    assert unknown_user.json() == wrong_password.json()


def test_me_rejects_missing_invalid_and_expired_tokens(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert (
        client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not-a-token"},
        ).status_code
        == 401
    )

    settings = get_settings()
    expired = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert response.status_code == 401


def test_invalid_email_is_rejected(client):
    response = register(client, email="not-an-email")
    assert response.status_code == 422


def test_password_whitespace_is_preserved(client):
    password = "  correct-horse-battery  "
    assert register(client, password=password).status_code == 201
    assert login(client, password=password).status_code == 200
    assert login(client, password=password.strip()).status_code == 401


def test_postgresql_duplicate_classification_requires_expected_constraint():
    duplicate = IntegrityError(
        "insert",
        {},
        SimpleNamespace(
            sqlstate="23505",
            diag=SimpleNamespace(constraint_name="uq_users_email"),
        ),
    )
    other_unique = IntegrityError(
        "insert",
        {},
        SimpleNamespace(
            sqlstate="23505",
            diag=SimpleNamespace(constraint_name="uq_users_other"),
        ),
    )
    foreign_key = IntegrityError(
        "insert",
        {},
        SimpleNamespace(sqlstate="23503", diag=SimpleNamespace(constraint_name=None)),
    )

    assert is_duplicate_email_error(duplicate)
    assert not is_duplicate_email_error(other_unique)
    assert not is_duplicate_email_error(foreign_key)


def test_unexpected_integrity_error_is_rolled_back_and_reraised():
    class BrokenSession:
        rollback_called = False

        def add(self, _user):
            pass

        def commit(self):
            raise IntegrityError("insert", {}, RuntimeError("foreign key failure"))

        def rollback(self):
            self.rollback_called = True

    db = BrokenSession()
    payload = RegisterRequest(
        email="new@example.com",
        password="correct-horse-battery",
    )

    with pytest.raises(IntegrityError):
        register_user(payload, db)
    assert db.rollback_called
