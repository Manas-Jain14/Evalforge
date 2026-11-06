# Product Requirements Document

**Status:** Product intent is **CONFIRMED** where stated below; technical details are marked **PROPOSED** or **UNRESOLVED**. This document describes a planned product, not implemented capabilities.

## 1. Product summary

EvalForge is a developer-first platform for understanding, monitoring, debugging, and investigating LLM-powered applications. Its central promise is: **Understand every trace. Investigate every failure.**

It records a complete request/workflow as a trace, its operations as spans, and notable occurrences as events. Developers should be able to inspect timing, relationships, failures, token consumption, estimated cost, unusual patterns, and the evidence behind a possible explanation.

EvalForge is not a chatbot, generic analytics dashboard, simple log viewer, prompt playground, or generic AI wrapper.

## 2. Users and needs

| User | Need |
|---|---|
| AI / generative AI engineer | Understand model calls, tool use, token use, latency, and failures in context |
| Backend engineer | See which application operation failed or caused a slow request |
| Agent/workflow developer | Reconstruct nested steps, retries, and relationships |
| Small AI team or startup | Diagnose operational behavior without maintaining a large observability stack |

## 3. Problem and outcomes

When an LLM application request fails or becomes slow/expensive, its execution may span retrieval, model calls, tools, and application code. A developer needs a trustworthy timeline and evidence, not merely a generated explanation.

### Desired outcomes

- Instrument generic Python operations with low overhead.
- Ingest SDK telemetry and historical JSON/JSONL through the same canonical pipeline.
- Explore trace structure, timing, errors, and events.
- Compute operational metrics deterministically.
- Request an optional AI investigation whose factual claims link to evidence.
- Keep customer data private by default and make external investigation transfer explicit.

No numerical scale, latency SLA, retention period, or availability target has been agreed; these are unresolved and must be set before production operation.

## 4. Core user journey

1. Register and authenticate.
2. Create a project and generate a project-scoped key (shown only once).
3. Install/configure the Python SDK and manually instrument a request, or upload JSON/JSONL history.
4. Inspect the resulting trace, nested spans, waterfall, events, and metrics.
5. Review deterministic overview and basic anomaly insights.
6. Explicitly request an investigation, review findings and their supporting trace/span references, and retain a report.

End-to-end continuity is more important than a broad but disconnected feature set.

## 5. MVP requirements

| Capability | Requirement |
|---|---|
| Accounts and projects | Register/login; project ownership enforced for all dashboard operations |
| API keys | Generate, list metadata, revoke; hash at rest and reveal secret once |
| Python SDK | Manual trace/span/event lifecycle, generic operations, optional model/token metadata, batching/flush |
| Historical upload | JSON and JSONL; parse and validate to canonical schema |
| Shared pipeline | Normalize, enforce relationships and idempotency, persist, report processing result |
| Exploration | Project trace list/detail with nested spans and timing; event search/list |
| Analytics | Volume, latency quantiles, error rate, token use, available estimated cost, basic deterministic insights |
| Investigation | On-demand Gemini with bounded evidence package, validated report, history |
| Operations | Tests, local Docker Compose/PostgreSQL setup, deployment instructions |

## 6. Product principles

1. Telemetry capture should not depend on AI availability.
2. Observed facts and generated hypotheses must be visibly distinct.
3. Every investigation fact should have evidence references.
4. Generic operations must work without provider/model/token metadata.
5. Project data must remain isolated.
6. The interface should feel like an engineering control room, not a generic AI template; see [Frontend Design](FRONTEND_DESIGN.md).

## 7. Success measures (proposed)

Validate during implementation; these are not targets yet:

- A new developer can go from project creation to visible SDK trace using the documented quickstart.
- Both SDK and file-upload paths produce equivalent canonical records.
- A trace can be reconstructed with correct parent relationships and durations.
- Duplicate handling follows the approved persistence policy; do not claim durable batch-level replay protection unless its persistence mechanism is approved and implemented.
- Deterministic metrics can be reconciled against fixture data.
- Investigation claims reference persisted evidence or clearly state insufficiency.
- Dashboard core functions remain usable when Gemini is unavailable.

## 8. Scope boundaries

Post-MVP: JavaScript/TypeScript SDK, automatic instrumentation, advanced OpenTelemetry integration, Kafka/Redis/Celery/distributed ingestion, microservices, advanced prompt/model comparison, regression evaluation, advanced alerting, automated remediation, and complex ML anomaly detection. The MVP uses a modular monolith and synchronous processing of reasonably sized uploads.

## 9. Assumptions and open product decisions

**Assumptions:** initial users are small engineering teams; each MVP project has one owner (no team-sharing model); initial SDK support is Python; users manually initiate investigations; deployment starts as one application and PostgreSQL.

**UNRESOLVED:** whether a future post-MVP release needs team sharing, account verification and password recovery, project deletion/retention policy, pricing/quotas, operational scale targets, detailed onboarding, and data residency. Resolve before the relevant production feature, not by inventing behavior.

See [MVP Scope](MVP_SCOPE.md), [Implementation Plan](IMPLEMENTATION_PLAN.md), and [Security](SECURITY.md).
