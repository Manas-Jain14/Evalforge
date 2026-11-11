# Deployment and Local Development

**Status:** Phase 1 local development uses the owner's existing native PostgreSQL 18 installation on Windows and the existing `evalforge` database. Production host, topology, retention, and operational targets are **UNRESOLVED**.

## Local development target

For Phase 1, PostgreSQL 18 is already installed natively and the owner has created `evalforge` through pgAdmin 4. Do not reinstall/configure the server or manually create application tables in pgAdmin; Alembic manages application schema changes. The FastAPI process runs from the Python virtual environment.

Windows PowerShell workflow:

1. Copy root `.env.example` to root `.env` if it does not exist.
2. Enter the local `postgres` role password in `DATABASE_URL` (URL-encode special characters) and set a local JWT secret.
3. Create and activate a Python virtual environment from `backend`.
4. Install `backend/requirements.txt`.
5. From `backend`, run `alembic upgrade head` against the configured `evalforge` database.
6. Start `uvicorn app.main:app --reload`; run `python -m pytest` separately.

The settings loader resolves `../.env` when commands run from `backend`. Confirm `DATABASE_URL` points to `evalforge` before applying migrations. Do not run migrations against another database without explicit approval.

## Configuration categories

Exact variable names are not yet fixed. Document names and validation in implementation; never include real values.

| Category | Examples of required configuration |
|---|---|
| Database | PostgreSQL URL/credentials |
| Auth | JWT signing/verification key, issuer/audience as selected |
| Gemini | API credential and selected model/configuration |
| API | Allowed origins, public endpoint/base URL, size/time limits |
| SDK | Hosted/local ingestion endpoint (client-side configuration) |
| Security | API-key hash pepper if selected; secret manager reference |

The root `.env.example` contains a password-free PostgreSQL URL and placeholder JWT secret. Production secrets belong in the host's secret manager, not source control, frontend bundles, or logs.

## Database and migrations

Use PostgreSQL with JSONB. Apply Alembic migrations as an explicit controlled step before serving new code. Never use application startup table creation. Backups and restore tests are required before production telemetry is considered durable. Restrict network access and use least-privilege credentials. Migration rollback/forward-fix procedures must be defined for the chosen host.

## Upload storage and retention

The initial `uploads` table stores metadata/status; no external object storage is assumed. The implementation must decide whether raw files are streamed/temporarily staged and promptly deleted or retained under a documented policy. Do not silently depend on ephemeral local disk for durable file storage. Set file size, processing time, retention, and cleanup policy before production use.

## Production readiness checklist

- Select hosting, domain/TLS, origins, and runtime process model.
- Configure secrets through managed secret storage and rotation.
- Set DB network policy, backups, restore test, migrations, monitoring, and alert ownership.
- Define user/project/telemetry/report retention and deletion.
- Set request/rate/usage limits and operational SLOs based on expected load.
- Set Gemini consent, redaction, region/provider settings, spend controls, and outage behavior.
- Verify logs redact credentials, raw prompts, and private telemetry.
- Document deploy, rollback/forward-fix, incident, key-revocation, and recovery runbooks.

## Health and observability (proposed)

Expose readiness/liveness checks that do not disclose secrets or internal topology. Log structured request IDs and safe operational metrics. Avoid logging payloads. Monitor DB health, ingestion failures/latency, upload rejection, Gemini failures/spend, and application errors, with retention/access controls.

## Unresolved deployment decisions

Hosting provider/region, public URL, TLS termination, process count, DB managed/self-hosted choice, backup RPO/RTO, telemetry retention, upload staging, log platform, rate-limit mechanism, availability targets, and operational ownership. These must be resolved before production deployment; the MVP can target local demo first.
