# ADR 007: Atomic ingestion with record-level idempotency

- **Status:** Accepted (approved by project owner)
- **Date:** 2026-11-06

## Context

The approved initial relational schema contains exactly eight logical tables: `users`, `projects`, `api_keys`, `traces`, `spans`, `events`, `uploads`, and `analysis_reports`. A prior design discussion identified a possible ninth `ingestion_batches` table to persist batch fingerprints and outcomes, but the project owner has not approved that schema expansion.

Telemetry may arrive from the Python SDK or historical JSON/JSONL uploads. Repeated delivery must not create duplicate trace/span/event records, and partial writes would make parent references and retries difficult to reason about.

## Decision

- Preserve exactly the eight approved logical tables. Do not add `ingestion_batches`.
- Validate the complete batch before writes and commit all new trace/span/event records in one transaction.
- Use stable trace, span, and event UUIDs as record identities.
- If an existing record ID has identical canonical content, treat it as an idempotent duplicate/no-op.
- If an existing record ID has different canonical content, reject the complete incoming batch and roll back all writes from that batch.
- Treat any supplied `batch_id` as request-correlation metadata only; do not claim durable batch-level deduplication or response recovery.

## Consequences

- SDK ingestion and historical uploads can share the same record-level identity rules.
- Database uniqueness constraints guard concurrent inserts; the service must compare normalized content and translate conflicts safely.
- There is no partial-success response.
- Replaying an empty batch cannot be recognized, and a previous batch response cannot be retrieved by batch ID.
- A batch containing already-persisted records plus new records may insert only the new records if all existing IDs match canonical content; the transaction still commits or rolls back as a whole.
- Exact API response shape, payload limits, and treatment of repeated IDs inside the same submitted batch must be finalized and tested before ingestion implementation.

## Revisit when

The project owner explicitly approves changing the eight-table schema and a concrete need for durable batch-level audit/replay is demonstrated. Any schema change requires an ADR update and Alembic migration; do not silently add a batch ledger.
