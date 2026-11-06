# ADR 005: Separate deterministic analytics from on-demand AI investigation

- **Status:** Accepted (separation and Gemini-only-on-demand direction confirmed)
- **Date:** 2026-11-06

## Context

Operational metrics should be reproducible and available independently of a third-party LLM. AI analysis may help investigate a selected issue but must be grounded in evidence and protect telemetry privacy.

## Decision

Compute volume, latency, errors, token use, estimated cost, and simple anomaly insights with Python/SQL. Use Gemini exclusively for explicit, user-initiated investigations. The backend selects a compact evidence package; Gemini has no database access. Unknown pricing is unavailable rather than guessed.

## Consequences

- Dashboard analytics continue during Gemini outages.
- Investigation results must distinguish observed facts from hypotheses and reference evidence.
- Raw prompts/responses are not captured by default; external data transfer requires appropriate consent and redaction.
- Unknown pricing remains unavailable, not zero. A fixed-precision cost amount with an explicit ISO 4217 currency and normalization to one reporting currency is **PROPOSED / UNRESOLVED**; USD is only a candidate, and no pricing catalog or conversion source is approved. Analytics must label currency and must not aggregate mixed currencies. See [Telemetry Schema](../TELEMETRY_SCHEMA.md).
- Pricing catalog, conversion rules, anomaly thresholds, token budgets, caching, and consent UX remain implementation-time decisions.

## Revisit when

User research or measured needs establish a new analysis capability. Automatic AI invocation in ingestion or dashboard refresh is not an implicit extension of this decision.
