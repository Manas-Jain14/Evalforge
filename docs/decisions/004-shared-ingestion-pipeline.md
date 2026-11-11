# ADR 004: Converge SDK and historical uploads on one pipeline

- **Status:** Accepted (shared-pipeline requirement confirmed; atomic and record-level idempotency policy confirmed in ADR 007)
- **Date:** 2026-11-06

## Context

SDK events and uploaded history must receive the same validation, normalization, integrity checks, persistence, duplicate handling, and analytics semantics.

## Decision

Keep transport adapters separate only through authentication and parsing. Both call one canonical ingestion service. The MVP processes reasonably sized uploads synchronously and does not introduce background infrastructure without a concrete need.

## Consequences

- One canonical persistence and analytics path.
- Consistent validation and project isolation.
- Exactly eight initial logical tables; do not add `ingestion_batches`.
- Process each batch atomically, all-or-nothing. Stable trace/span/event IDs provide record-level idempotency: identical canonical content is a no-op; conflicting content rejects and rolls back the entire batch.
- Batch IDs are correlation metadata only; no batch response ledger or empty-batch replay detection is provided.
- Exact limits, duplicate response representation, and raw-file staging remain unresolved and must be finalized before contract freeze.

## Revisit when

Measured batch size/latency or reliability needs show synchronous handling cannot meet documented requirements. Any queue proposal must include a concrete workload and operational cost.
