from app.core.config import Settings


def test_settings_load_root_env_when_working_directory_is_backend(tmp_path, monkeypatch):
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    (tmp_path / ".env").write_text(
        "APP_ENV=development\n"
        "DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/evalforge\n"
        "JWT_SECRET_KEY=test-only-secret-key-at-least-32-bytes-long\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(backend_dir)
    for name in (
        "APP_ENV",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings()

    assert settings.database_url.get_secret_value() == (
        "postgresql+psycopg://postgres@localhost:5432/evalforge"
    )
