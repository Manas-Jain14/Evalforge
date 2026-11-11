import sqlite3

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def is_duplicate_email_error(exc: IntegrityError) -> bool:
    original = exc.orig
    if getattr(original, "sqlstate", None) == "23505":
        diagnostic = getattr(original, "diag", None)
        return getattr(diagnostic, "constraint_name", None) == "uq_users_email"
    return (
        isinstance(original, sqlite3.IntegrityError)
        and str(original) == "UNIQUE constraint failed: users.email"
    )


def register_user(payload: RegisterRequest, db: Session) -> User:
    user = User(email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if is_duplicate_email_error(exc):
            raise DuplicateEmailError from None
        raise
    db.refresh(user)
    return user


def login_user(payload: LoginRequest, db: Session, settings: Settings) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    stored_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    if not verify_password(payload.password, stored_hash) or user is None:
        raise InvalidCredentialsError
    return user, create_access_token(user.id, settings)
