# ADR 004: Converge SDK and historical uploads on one pipeline

- **Status:** Accepted (shared-pipeline requirement confirmed; detailed failure policy unresolved)
- **Date:** 2026-11-06

## Context

SDK events and uploaded history must receive the same validation, normalization, integrity checks, persistence, duplicate handling, and analytics semantics.

## Decision

Keep transport adapters separate only through authentication and parsing. Both call one canonical ingestion service. The MVP processes reasonably sized uploads synchronously and does not introduce background infrastructure without a concrete need.

## Consequences

- One canonical persistence and analytics path.
- Consistent validation and project isolation.
- Safe retries require an approved idempotency design. The confirmed eight-table schema does not contain a durable SDK batch record.
- A proposed ninth `ingestion_batches` table is the recommended durable batch-level option, but is **UNRESOLVED pending project-owner approval**. Stable record IDs are the within-eight-table fallback and cannot identify empty-batch replay or complete batch outcomes; see [Database Schema](../DATABASE_SCHEMA.md).
- Atomic versus partial batch acceptance, duplicate conflict behavior, exact limits, and raw-file staging remain unresolved and must be finalized before contract freeze.

## Revisit when

Measured batch size/latency or reliability needs show synchronous handling cannot meet documented requirements. Any queue proposal must include a concrete workload and operational cost.
