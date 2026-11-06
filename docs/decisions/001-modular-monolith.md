# ADR 001: Use a modular monolith

- **Status:** Accepted (architecture direction confirmed)
- **Date:** 2026-11-06

## Context

EvalForge needs authentication, project/key management, ingestion, telemetry, uploads, analytics, investigations, and report history. The delivery window is about 30 focused hours. Independent services would add deployment, networking, consistency, and operational overhead before scale is established.

## Decision

Use one FastAPI backend organized into independently testable logical modules. Modules share a PostgreSQL database and application process; boundaries are code organization, not microservices.

## Consequences

- Faster local development and end-to-end delivery.
- Shared transactions and direct domain service calls are possible.
- Boundaries and tests must prevent accidental coupling.
- Scale/deployment is initially simpler, but modules are not independently deployable.
- Do not add Kafka, Redis, Celery, Kubernetes, or services absent a measured requirement.

## Revisit when

Measured load, isolation, independent scaling, or operational ownership makes a specific module a real deployment boundary. Re-evaluate with evidence, not anticipated scale alone.
