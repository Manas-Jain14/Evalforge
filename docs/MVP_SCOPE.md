# MVP Scope and Prioritization

**Status:** Scope boundaries in this document reflect the agreed MVP direction. Individual acceptance criteria are proposed and should be tested during implementation.

## MVP objective

Deliver one demonstrable workflow from account/project setup through Python instrumentation or historical upload, trace inspection, deterministic metrics, and an explicitly requested evidence-backed investigation.

## Delivery target and priority (not product scope)

The approximately 30-hour development window targets a demonstrable prototype/MVP, **not** a fully production-hardened observability platform. All capabilities in the MVP scope below remain in scope; this ordered list determines what to build first, not what is removed:

1. Authentication and project creation.
2. Database migrations.
3. One canonical trace ingestion path.
4. Trace and span retrieval.
5. A basic but distinctive frontend.
6. Python SDK.
7. Historical uploads.
8. Deterministic analytics.
9. Gemini investigation if the remaining time permits.

Gemini remains an MVP capability, but it is last in delivery priority and may be deferred if the time budget is exhausted. This is a prototype delivery tradeoff, not a change to the approved product scope. Production hardening, operational reliability, retention, recovery, scale targets, and deployment readiness require additional decisions and time.

## In scope

1. Authentication and project management with owner checks.
2. Project-scoped API key create/list/revoke; key shown once, hash at rest.
3. Manual Python SDK trace/span/event instrumentation for generic operations.
4. JSON and JSONL historical telemetry upload.
5. Shared validation/normalization/ingestion pipeline with the explicitly approved idempotency policy.
6. PostgreSQL trace/span/event persistence and project-safe relationships.
7. Trace explorer/detail with nested spans and waterfall; event explorer.
8. Deterministic overview/latency/usage analytics and basic explainable anomaly insights.
9. User-initiated Gemini investigations and persisted reports with evidence references.
10. Basic frontend, tests, local Docker Compose setup, and deployment documentation.

Durable batch-level idempotency is not implementable from the current eight-table proposal alone. The recommended ledger is a proposed ninth table and requires owner approval; until then, document the limitations of a record-level stable-ID fallback. See [Database Schema](DATABASE_SCHEMA.md).

## Excluded from MVP

- JavaScript/TypeScript SDK.
- Automatic instrumentation and advanced OpenTelemetry integration.
- Kafka, Redis, Celery, Kubernetes, distributed ingestion, microservices.
- Advanced prompt/model comparisons and regression evaluation.
- Advanced alerting or automated remediation.
- Complex ML anomaly detection.
- Assumed external object storage.

## Slice order

| Slice | Demonstrable exit condition |
|---|---|
| Identity and migrations | Authentication, single-owner project creation, and local migrations work |
| Canonical path | One trace ingestion path persists a trace and spans using the canonical schema |
| Retrieval | Project-scoped trace and span retrieval returns the persisted hierarchy |
| Basic distinctive frontend | User can create/select a project and inspect a trace in the agreed EvalForge visual direction |
| Python SDK | Manual nested trace works; flush/retry is bounded and failures visible |
| Historical uploads | JSON/JSONL uploads enter the same canonical pipeline |
| Deterministic analytics | Fixture-backed volume, quantiles, error/token metrics, and labeled known/unknown cost |
| Gemini investigation (if time permits) | Explicit request yields validated findings with evidence references or a clear insufficient-evidence outcome |
| Prototype validation | Integration/security checks and a repeatable demo; production gaps are stated |

The exact dependencies and order are described in [Implementation Plan](IMPLEMENTATION_PLAN.md).

## MVP acceptance checklist (proposed)

- An unowned project/trace/key cannot be read or changed by another user.
- SDK project identity derives only from key verification.
- Idempotency behavior matches the approved persistence design; claim batch-level replay/conflict guarantees only if the ledger is approved and implemented, otherwise document the record-level fallback limitations.
- JSON/JSONL and SDK data normalize to the same canonical semantics.
- Parent span/event relationships cannot cross trace or project.
- Duration/token constraints are enforced; generic spans need no model fields.
- Analytics are deterministic and independent of Gemini.
- Unknown pricing is unavailable, not fabricated.
- AI is called only after an authorized user action and privacy checks.
- Reports separate observed facts from hypotheses and cite evidence.
- No prompt/response capture or external transfer is enabled by default.
- Application has useful behavior when Gemini is unavailable.

## Time constraint and tradeoffs

The planning envelope is about one month at roughly one hour/day (~30 focused hours), targeting a demonstrable prototype/MVP rather than a fully production-hardened platform. This is a severe constraint: prefer one-user-owned project model, bounded synchronous requests, simple deterministic heuristics, and a basic distinctive frontend. Implement in the delivery priority above; Gemini can be deferred if earlier work consumes the budget. The estimate excludes unspecified deployment/operations and production-hardening complexity and is not a guarantee. Re-scope rather than add infrastructure when estimates exceed time.

## Dependencies and unresolved scope

Confirm password recovery/verification needs, supported Python versions, upload size/count, retention, external-data consent UX, target deployment, and cost-pricing update process before those features. The MVP's single-owner project model is established; any future team-sharing model is outside this scope and remains unresolved. If time slips, preserve security, canonical ingestion, trace visibility, and honest deterministic metrics; defer UI polish rather than weaken isolation or evidence quality.

See [PRD](PRD.md), [Security](SECURITY.md), and [Implementation Plan](IMPLEMENTATION_PLAN.md).
