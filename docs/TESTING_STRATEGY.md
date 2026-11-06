# Testing Strategy

**Status:** pytest for backend/SDK is **CONFIRMED**. Frontend test tooling and coverage thresholds are **UNRESOLVED** until implementation chooses a stack.

## Testing principles

- Test behavior and trust boundaries, not only happy-path serialization.
- Keep tests deterministic and isolated; use synthetic fixtures, never customer telemetry.
- Validate source parity: SDK-shaped batches and JSON/JSONL feed identical canonical semantics.
- Measure actual behavior and report only commands that were run.
- Prefer targeted tests during development, then integration/end-to-end checks at milestones.

## Backend

- Unit: Pydantic validation, normalization, status derivation, cost/quantile/insight functions, error mapping, evidence schema validation.
- Database integration (PostgreSQL): constraints, composite FKs (including same-project/trace span references and project-owner references), migrations, approved idempotency behavior, transaction rollback, project/time indexes where useful.
- API: auth, ownership, key create-once/revoke, pagination/filter validation, cross-project denial, size limits, safe errors.
- Ingestion: JSON/JSONL parse, schema versions, reference/cycle validation, partial/atomic policy, status accuracy, and the explicitly approved duplicate policy. **UNRESOLVED:** if the owner approves a ninth `ingestion_batches` table, test durable batch replay, fingerprint conflict, concurrent requests, and atomic ledger/telemetry commit; without it, test only the chosen record-level stable-ID behavior and document that empty-batch and complete-batch replay cannot be detected. Do not claim or test durable batch-level idempotency without supporting approved persistence. See [Database Schema](DATABASE_SCHEMA.md) and [Ingestion Pipeline](INGESTION_PIPELINE.md).
- Investigation: no database access from Gemini adapter, explicit-only invocation, redaction/consent gate, bounded evidence, timeout and invalid response behavior.

## Python SDK

Test trace/span lifecycle, nesting and exception capture, monotonic duration, UTC serialization, optional model/token fields, generic operations, context propagation in supported concurrency modes, buffer bounds, flush/close, retry classification/backoff, stable batch-ID reuse consistent with the approved persistence policy, and secret/prompt redaction. Do not treat client-side batch IDs alone as durable idempotency; batch-level replay guarantees depend on approval and implementation of the proposed ledger.

## Frontend

Choose an appropriate React/TypeScript test runner when implementation begins. Cover navigation/project context, loading/empty/error states, filters, trace/span selection and links, report evidence display, one-time API key UX, theme switching, keyboard access, semantic states, and responsive layouts. Add accessibility/contrast checks; do not claim compliance based only on automated scans.

## End-to-end and deployment

Use Docker Compose with PostgreSQL for a clean-start smoke test: migrate, register, create project/key, emit SDK telemetry, inspect trace/events/metrics, upload equivalent JSONL, and, if the last-priority investigation capability is implemented, request an investigation with a stubbed Gemini boundary and inspect its report. Test service behavior when Gemini is unavailable. Verify startup configuration fails clearly when required secrets are absent, and logs/errors contain no credentials.

## Fixtures and CI

Use small versioned synthetic traces representing nested/parallel spans, errors, retries, missing model metadata, unknown price, repeated stable record IDs, malformed data, and sparse analytics windows. Add duplicate-batch/fingerprint fixtures only if a durable ledger is approved. Verify unknown cost is unavailable rather than zero, and that analytics never combine mixed currencies or omit currency labels. CI commands and required services should be documented once established. No coverage percentage is agreed; avoid a vanity threshold until baseline exists.

## Release gate (proposed)

- Relevant unit and integration suites pass.
- Migrations apply from an empty DB.
- Cross-project tests pass on all resource families.
- Upload limits and ingestion replay policy verified.
- Analytics reconciled to hand-calculated fixtures.
- If investigation is implemented, Gemini calls are gated and output schema/evidence are validated.
- Frontend core keyboard/theme states reviewed.
- Known risks and unrun tests are disclosed.
