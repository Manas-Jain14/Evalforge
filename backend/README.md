# Backend Development

Phase 1 provides registration/login/current-user endpoints and owner-scoped project create/list/read/update. Only `users` and `projects` are migrated; telemetry, API keys, SDK, uploads, analytics, investigations, and frontend are not implemented.

## Configuration

PostgreSQL 18 is already installed natively on the owner's Windows machine, and the `evalforge` database has already been created through pgAdmin 4. Do not reinstall/configure PostgreSQL or create application tables in pgAdmin; Alembic owns schema creation.

From the repository root, copy `.env.example` to `.env` if it does not already exist. Edit `DATABASE_URL` to enter the local password for role `postgres`, URL-encoding special characters, and replace `JWT_SECRET_KEY` with a local random secret of at least 32 bytes. Never commit `.env` or use the example JWT secret outside local development. The backend configuration loader reads `../.env` when commands run from `backend`.

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development`, `test`, or `production` |
| `DATABASE_URL` | SQLAlchemy URL for the existing local `evalforge` database using role `postgres`; insert the URL-encoded local password |
| `JWT_SECRET_KEY` | HMAC signing secret; at least 32 bytes |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token expiry, default 30; allowed range 1–60 |

Configuration is validated when the application starts. The application does not create tables automatically.

## Windows PowerShell setup

PostgreSQL must already be running locally and the `evalforge` database must exist. From the repository root:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Edit .env: add the local postgres password to DATABASE_URL and set JWT_SECRET_KEY.
# Example: postgresql+psycopg://postgres:URL_ENCODED_PASSWORD@localhost:5432/evalforge
# URL-encode special characters in the password.
Set-Location backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Run tests in a second terminal from `backend`, with the virtual environment activated:

```powershell
python -m pytest
```

Tests use isolated SQLite databases for fast request/model checks. Do not run Alembic against a test database as part of this setup; apply migrations only to the owner's `evalforge` database after confirming the connection URL. PostgreSQL 18 is the intended development/runtime database.

## API

- `GET /health` — application liveness.
- `POST /api/v1/auth/register` — create an account.
- `POST /api/v1/auth/login` — return a bearer access token.
- `GET /api/v1/auth/me` — current user.
- `POST /api/v1/projects` — create an owned project.
- `GET /api/v1/projects?offset=0&limit=50` — list owned projects.
- `GET /api/v1/projects/{project_id}` — retrieve an owned project.
- `PATCH /api/v1/projects/{project_id}` — update project name/description.

The interactive OpenAPI documentation is available at `/docs`.

## Provisional choices requiring owner review

The product docs leave these details unresolved; this Phase 1 implementation uses small, explicit defaults:

- Email is trimmed and lowercased before uniqueness checks.
- Passwords require 12–128 characters and use Argon2id through `pwdlib`.
- JWTs are HS256 bearer access tokens with `sub`, `iat`, and `exp`, defaulting to 30 minutes; there is no refresh-token system.
- Project listing uses bounded offset pagination (default 50, maximum 100).
- Unknown request fields are rejected, and an inaccessible project returns 404.
- User/project deletion is not exposed; the user/project foreign key currently restricts deleting a user with owned projects rather than cascading. Confirm retention/deletion behavior before adding delete operations.

Confirm these choices before treating the API as a stable external contract.

Login/registration rate limiting is not implemented in this foundation; the docs leave thresholds and mechanism unresolved. Add and test an approved control before production exposure.
