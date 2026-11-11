from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    database_url: SecretStr
    jwt_secret_key: SecretStr
    jwt_access_token_expire_minutes: int = 30

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 bytes")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
        except ArgumentError as exc:
            raise ValueError("DATABASE_URL must be a valid SQLAlchemy URL") from exc
        if url.drivername not in {"postgresql+psycopg", "sqlite+pysqlite"}:
            raise ValueError("DATABASE_URL must use PostgreSQL with psycopg or SQLite for tests")
        return value

    @field_validator("jwt_access_token_expire_minutes")
    @classmethod
    def validate_token_expiry(cls, value: int) -> int:
        if not 1 <= value <= 60:
            raise ValueError("JWT access-token expiry must be between 1 and 60 minutes")
        return value

    @model_validator(mode="after")
    def reject_example_secret_in_production(self) -> "Settings":
        if self.app_env != "test" and self.database_url.get_secret_value().startswith("sqlite"):
            raise ValueError("SQLite is allowed only in the test environment")
        if self.app_env == "production" and "replace-with-" in self.jwt_secret_key.get_secret_value():
            raise ValueError("A real JWT_SECRET_KEY is required in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
