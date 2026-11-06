# Deployment and Local Development

**Status:** Docker Compose and PostgreSQL for local development are **CONFIRMED**. Production host, topology, retention, and operational targets are **UNRESOLVED**. No deployment configuration or application currently exists in this documentation-only repository.

## Local development target

The initial local environment should run the FastAPI application, PostgreSQL, and React frontend with Docker Compose or documented local equivalents. Keep the MVP as one backend deployment and one PostgreSQL database; do not add a queue, cache, object store, or orchestration system without a concrete requirement.

Expected developer workflow once implementation exists:

1. Copy placeholder names from `.env.example` into a local untracked environment file.
2. Start PostgreSQL and application processes via documented Compose commands.
3. Apply Alembic migrations explicitly.
4. Run pytest/backend, SDK, and frontend test commands.
5. Exercise a synthetic trace ingestion and dashboard query.

These are proposed steps, not commands verified in the current repository.

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

`.env.example`, if created during implementation, must contain placeholders only. Production secrets belong in the host's secret manager, not image layers, source control, frontend bundles, or logs.

## Database and migrations

Use PostgreSQL with JSONB. Apply Alembic migrations as an explicit controlled step before serving new code. Backups and restore tests are required before production telemetry is considered durable. Restrict network access and use least-privilege credentials. Migration rollback/forward-fix procedures must be defined for the chosen host.

## Upload storage and retention

The initial `uploads` table stores metadata/status; no external object storage is assumed. The implementation must decide whether raw files are streamed/temporarily staged and promptly deleted or retained under a documented policy. Do not silently depend on local container disk for durable file storage. Set file size, processing time, retention, and cleanup policy before production use.

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
