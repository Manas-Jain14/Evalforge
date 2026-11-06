# API Contracts

**Status:** `/api/v1/` and the endpoint names below are **CONFIRMED proposed names**. Payload details are deliberately illustrative where not finalized. Do not treat examples as a frozen wire contract.

## Conventions

- REST, JSON request/response, Pydantic boundary schemas, FastAPI OpenAPI.
- Versioned base path `/api/v1/`.
- Dashboard endpoints use a user JWT; ingestion uses a project API key; uploads use JWT plus project ownership.
- SDK project identity is resolved server-side from the API key. Ignore/reject client-supplied project identity for authorization.
- Lists require pagination and bounded filters/sorts; exact cursor/offset convention and defaults are **UNRESOLVED**.
- Apply request/file size limits. Use consistent structured errors and never disclose secrets or cross-project object existence.

### Proposed error envelope

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request could not be processed.",
    "details": []
  }
}
```

Codes/status mapping proposal: `400` malformed input, `401` missing/invalid credentials, `403` authorization denied, `404` absent or inaccessible resource, `409` duplicate/conflicting idempotency key when the approved persistence design detects it, `413` body/file too large, `422` schema/semantic validation, `429` rate limit, `500` unexpected server failure, `502`/`503` external investigation dependency failure. Do not imply batch-level `409` detection is available with the current eight-table schema. See [Ingestion Pipeline](INGESTION_PIPELINE.md). Exact mapping requires implementation finalization.

## Authentication

| Method and path | Auth | Responsibility / contract expectation |
|---|---|---|
| `POST /api/v1/auth/register` | Public, rate-limited | Validate email/password, create user, return safe account representation; never return password/hash |
| `POST /api/v1/auth/login` | Public, rate-limited | Verify credentials, issue short-lived JWT; avoid account enumeration |
| `GET /api/v1/auth/me` | User JWT | Return current authenticated user profile |

JWT claims, expiry, refresh/session strategy, and registration verification are unresolved. See [Security](SECURITY.md).

## Projects and API keys

| Method and path | Auth | Responsibility / contract expectation |
|---|---|---|
| `POST /api/v1/projects` | User JWT | Create project owned by caller; accept name and optional description |
| `GET /api/v1/projects` | User JWT | Paginated list of caller-owned projects |
| `GET /api/v1/projects/{id}` | User JWT + owner check | Read one owned project |
| `PATCH /api/v1/projects/{id}` | User JWT + owner check | Update allowed project metadata only |
| `POST /api/v1/projects/{id}/api-keys` | User JWT + owner check | Generate key; return secret exactly once |
| `GET /api/v1/projects/{id}/api-keys` | User JWT + owner check | List metadata, never secret/hash |
| `DELETE /api/v1/api-keys/{id}` | User JWT + key-project owner check | Revoke key; idempotent semantics to finalize |

Return key ID, non-secret prefix, creation/revocation metadata. Never return stored hashes. A project ID supplied by the browser is a resource selector, not proof of authorization.

## SDK ingestion

`POST /api/v1/ingest/batch` uses project API-key authentication (`Authorization: Bearer ...` proposed). It accepts a bounded batch containing `schema_version`, `batch_id`, `traces`, `spans`, and `events`, then validates/normalizes through the shared pipeline. The proposed response may include accepted/rejected status and counts, but persistent batch replay and changed-payload conflict detection are **UNRESOLVED**: the confirmed eight-table schema has no SDK batch ledger. The recommended `ingestion_batches` table is a proposed ninth table and requires project-owner approval. Until then, record-level stable-ID behavior is only a fallback and cannot identify empty-batch replay or complete batch outcomes. Exact shape, atomicity, response codes for partial failures, and retry contract require finalization. See [Ingestion Pipeline](INGESTION_PIPELINE.md), [Database Schema](DATABASE_SCHEMA.md), and [SDK Specification](SDK_SPECIFICATION.md).

## Historical uploads

| Method and path | Auth | Responsibility / contract expectation |
|---|---|---|
| `POST /api/v1/projects/{id}/uploads` | User JWT + owner check | Accept JSON or JSONL upload; validate size/format/schema; process synchronously when within limits; return upload status |
| `GET /api/v1/projects/{id}/uploads` | User JWT + owner check | Paginated upload metadata/status |
| `GET /api/v1/projects/{id}/uploads/{upload_id}` | User JWT + owner check | Read status and sanitized processing summary |

Multipart versus raw-body format, exact limits, temporary storage, and whether a failed attempt is retained as metadata are unresolved. Upload project is selected in URL and authorized through dashboard ownership; it must not be trusted without that check.

## Telemetry reads

| Method and path | Auth | Responsibility / common filters |
|---|---|---|
| `GET /api/v1/projects/{id}/traces` | User JWT + owner check | Paginated traces; proposed time range, status, environment, service, sort |
| `GET /api/v1/projects/{id}/traces/{trace_id}` | User JWT + owner check | Trace, nested spans, related events; ensure trace belongs to project |
| `GET /api/v1/projects/{id}/events` | User JWT + owner check | Paginated events; proposed time/type/trace filters and sort |

Return canonical schema fields from [Telemetry Schema](TELEMETRY_SCHEMA.md), with safe attribute redaction. Avoid returning unbounded nested data.

## Analytics

| Method and path | Auth | Responsibility |
|---|---|---|
| `GET /api/v1/projects/{id}/analytics/overview` | User JWT + owner check | Trace volume, latency summaries, error rate, tokens, cost availability for a selected period |
| `GET /api/v1/projects/{id}/analytics/latency` | User JWT + owner check | Time-bucketed latency and percentiles, with documented sample counts |
| `GET /api/v1/projects/{id}/analytics/usage` | User JWT + owner check | Token usage and backend-estimated cost, grouped by supported dimensions; cost must include an explicit currency and unknown pricing is unavailable, not zero |
| `GET /api/v1/projects/{id}/analytics/insights` | User JWT + owner check | Deterministic anomaly/operational insights with metric window and comparison basis |

Date range, timezone display, bucket boundaries, insufficient-sample behavior, and query limits must be finalized. Cost currency is **PROPOSED / UNRESOLVED**: use a fixed-precision amount with an explicit ISO 4217 code and normalize to one reporting currency only after choosing the currency and any conversion policy. USD is only a candidate, not an approved choice. Analytics must label currency, never sum mixed currencies, and represent unknown pricing as unavailable rather than zero. Metrics are deterministic and remain available without Gemini. See [Telemetry Schema](TELEMETRY_SCHEMA.md).

## AI investigations

| Method and path | Auth | Responsibility |
|---|---|---|
| `POST /api/v1/projects/{id}/investigations` | User JWT + owner check | Explicitly request investigation with a question and bounded optional scope; verify privacy/consent controls before Gemini call |
| `GET /api/v1/projects/{id}/investigations` | User JWT + owner check | Paginated report history |
| `GET /api/v1/projects/{id}/investigations/{report_id}` | User JWT + owner check | Read saved report and evidence references |

Investigation result contains summary, findings, evidence references, trace/span IDs, strength/confidence, possible explanations, recommendations, relevant metrics, and model/token metadata where appropriate. Async job model is not planned for MVP; timeout behavior and maximum evidence/token budgets remain implementation decisions. Gemini cannot access the database.

## Validation and API operations

Every route must validate types, range/size limits, ownership, and project relationships. Query filters must be allowlisted; sort fields must not become arbitrary SQL. OpenAPI should document auth schemes, schemas, pagination, and known errors. Request IDs and safe structured server logs are recommended; no credential, full API key, raw prompt, or unredacted sensitive payload logging.

## API-wide unresolved items

Pagination convention, exact schemas, payload size, rate limits, API key prefix format, JSONL framing, batch-level idempotency persistence/duplicate conflict response, cost reporting currency/conversion, report synchronous timeout strategy, token refresh, and compatibility/deprecation policy must be decided before API freeze. Do not invent details merely to fill a schema.
