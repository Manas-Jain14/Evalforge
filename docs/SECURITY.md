# Security and Privacy

**Status:** Security requirements in this document are **CONFIRMED**. Concrete algorithms, limits, retention, deployment controls, and consent UX requiring choices are identified as proposals or unresolved.

## Threat boundaries

Protect user credentials, project API keys, telemetry, uploaded files, investigation questions/reports, database access, and Gemini-bound evidence. Treat dashboard clients, SDK payloads, uploaded files, JSON attributes, and model output as untrusted. The principal authorization boundary is the project.

## Authentication and credentials

### Passwords

Use a modern adaptive password hash (Argon2id is **PROPOSED**, subject to deployment/library review); never plaintext, reversible encryption, or logs. Validate password policy and rate-limit login/register. Avoid account enumeration in authentication errors. Recovery, verification, MFA, and account lifecycle are **UNRESOLVED**.

### Dashboard JWT

JWTs are the proposed dashboard authentication mechanism. Sign with a managed secret or asymmetric key, validate signature/issuer/audience/expiry, use short-lived access tokens, and keep token storage/transmission safe. HTTPS is required in deployment. Do not put secrets or sensitive telemetry in claims. Refresh/revocation/session strategy, algorithm/key rotation, cookie versus bearer transport, and concrete lifetimes are **UNRESOLVED**; document and test them before production.

### Project API keys

Generate high-entropy random keys. Show full key only at creation, then store only a verification-safe hash (never plaintext), non-secret ID/prefix, project ID, creation/use/revocation metadata. Compare hashes safely. Revoke promptly and reject revoked keys. Consider keyed hashing/pepper managed outside the database; algorithm and rotation procedure need finalization. Never include full credentials in API responses after creation, logs, analytics, screenshots, or examples.

## Authorization and project isolation

- Resolve SDK project from the verified key record; never trust payload `project_id`.
- Every dashboard project operation checks authenticated ownership, including list/detail, upload, trace/event/analytics, report, and key routes.
- Add project filters to every query and project-aware foreign keys to telemetry relationships.
- Treat inaccessible object IDs as not found or deny consistently without leaking cross-project existence.
- Upload URL project is only a selector and requires ownership validation.
- The MVP uses a single-owner project model, not team membership. Proposed composite foreign keys can enforce that `uploads(project_id, submitted_by_user_id)` and `analysis_reports(project_id, requested_by_user_id)` match `(projects.id, projects.owner_user_id)`, provided the referenced project pair has an explicit unique constraint. These constraints protect stored relationships but do not authenticate the caller or replace mandatory application-level ownership checks on every operation.

## Input and upload protection

Use Pydantic validation and explicit semantic checks for UUIDs, timestamps, relationships, nonnegative duration/tokens, and bounded JSON attributes. Restrict supported formats to JSON/JSONL; validate actual content rather than trusting filename/MIME. Set configurable body/file, line, record-count, nesting, string, and processing-time limits. Reject malformed/unsupported schema versions and path-like filenames. Never execute uploaded content.

MVP upload processing is synchronous for reasonably sized files; no object store is assumed. Temporary-file location, permissions, cleanup, malware scanning requirement, and retention are **UNRESOLVED**. Avoid keeping raw upload content unless a reviewed requirement demands it.

## Privacy and redaction

- Do not capture raw prompts or model responses by default.
- SDK attributes, messages, exception strings, and uploaded data may contain personal data or secrets; provide redaction/opt-in controls and conservative bounds.
- Make data sent to Gemini explicit and consent-aware; never send private telemetry without appropriate user consent.
- Send a compact, relevant evidence package, not a raw database dump.
- Minimize investigation question, telemetry, and report retention; define deletion/retention policy before production.
- Do not log request bodies, passwords, API keys, JWTs, raw prompts, or unredacted telemetry.

Exact opt-in model, redaction rules, sensitive-field classification, data residency, and retention remain unresolved.

## Gemini boundary

Gemini is called only for explicit investigations, never SDK capture, ingestion, deterministic analytics, or ordinary dashboard refresh. Backend mediates all access and data selection. Validate structured responses against a strict schema; treat output as untrusted and distinguish facts from hypotheses. Apply input/output token budgets and timeouts. Do not execute recommendations or use output as authorization. Handle timeout/invalid output without corrupting telemetry or representing failure as a successful report.

## Rate limiting and abuse

Rate-limit login, key-authenticated ingestion, upload, report generation, and costly queries. Enforce per-project/user request and payload quotas. Numeric thresholds, storage budgets, and protection provider are **UNRESOLVED**; use measured configurable controls and return structured `429` responses.

## Secrets and configuration

Read secrets from environment or a secret manager; never hardcode, commit real `.env` files, print values, or expose them in frontend builds. `.env.example` may contain placeholders only when application setup is implemented. Rotate compromised JWT signing keys, DB credentials, Gemini credentials, and key-hash peppers using a documented runbook. Do not add actual secret values to this documentation.

## CORS, transport, database

Use HTTPS outside local development. Configure CORS to explicit trusted dashboard origins; do not combine wildcard origins with credentials. Restrict database network access to application hosts, least-privilege DB credentials, encrypted backups where available, and parameterized ORM queries. Apply migrations through a controlled deployment step. Avoid exposing DB or admin consoles publicly.

## Errors and monitoring

Return safe structured errors with no stack trace, SQL, tokens, key hashes, or provider credentials. Log correlation IDs, action/outcome, and sanitized diagnostics. Protect logs and define retention. Do not turn unexpected exceptions into success-shaped responses.

## Security validation checklist

Test cross-project access for every route, key hashing and revocation, expired/invalid JWTs, brute-force/rate limits, malformed and oversized JSON/JSONL, path/MIME spoofing, unsafe attributes, replay/conflict behavior, DB isolation, Gemini consent/redaction and timeout, invalid model output, and secret-free logs/errors.

Open decisions are tracked in [API Contracts](API_CONTRACTS.md), [Database Schema](DATABASE_SCHEMA.md), and [Deployment](DEPLOYMENT.md).
