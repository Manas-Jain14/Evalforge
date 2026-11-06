# ADR 003: Define one canonical telemetry schema

- **Status:** Accepted (canonical trace/span/event model confirmed; exact wire schema remains proposed)
- **Date:** 2026-11-06

## Context

Telemetry arrives from a Python SDK and historical JSON/JSONL files. Separate schemas or storage paths would lead to inconsistent UI and analytics.

## Decision

Normalize each source to shared Trace, Span, and Event entities. A trace is a complete workflow; a span is an individual operation; an event is an occurrence associated with a trace and optionally a span. UUIDs, UTC timestamps, JSONB attributes, nonnegative durations/tokens, and optional provider/model fields are required design properties.

## Consequences

- Source adapters may differ in auth and parsing but converge before persistence/analytics.
- Generic Python operations remain representable without model metadata.
- Parent relationships and project consistency require validation and database constraints.
- Cost currency representation and a canonical reporting-currency/conversion policy remain **PROPOSED / UNRESOLVED**; see [Telemetry Schema](../TELEMETRY_SCHEMA.md).
- Exact field names, status vocabulary, and detailed versioned payload are still to be finalized; this ADR does not freeze them.

## Revisit when

An interoperability requirement or implementation evidence warrants schema evolution. Use explicit schema versions and compatibility decisions.
