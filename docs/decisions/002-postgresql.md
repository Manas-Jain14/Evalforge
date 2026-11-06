# ADR 002: Use PostgreSQL as the system of record

- **Status:** Accepted (database choice confirmed)
- **Date:** 2026-11-06

## Context

EvalForge stores relational ownership and trace/span/event relationships alongside flexible telemetry attributes and investigation findings.

## Decision

Use PostgreSQL, JSONB for extensible metadata, SQLAlchemy ORM, and Alembic migrations.

## Consequences

- Relational constraints and transactions protect project and parent-child integrity.
- JSONB supports evolving attributes without a separate telemetry store.
- Use timezone-aware timestamps, UUIDs, and indexes based on actual query patterns.
- Schema evolution is migration-managed; avoid hidden runtime schema creation.
- PostgreSQL is required for local development and integration testing.

## Revisit when

Measured query/retention scale demonstrates a limitation that cannot be addressed with appropriate schema, indexes, or partitioning. No alternative database is currently approved.
