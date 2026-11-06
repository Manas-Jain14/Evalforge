# EvalForge

**Understand every trace. Investigate every failure.**

EvalForge is a planned developer-first platform for observing, debugging, and investigating applications powered by large language models. It is intended to make requests, operations, failures, latency, token usage, estimated cost, and supporting evidence understandable in one place.

> **Project status: Planned.** This repository currently contains documentation only. No application capabilities described here should be treated as implemented.

## The problem

LLM-powered applications often combine model calls, retrieval, tools, database access, and application code. When a request is slow, expensive, or incorrect, developers need to reconstruct what ran and where it failed. EvalForge's goal is to capture that workflow as traces, spans, and events, then pair deterministic operational metrics with explicitly requested, evidence-backed AI investigations.

EvalForge is not intended to be a chatbot, generic analytics dashboard, simple log viewer, prompt playground, or generic AI wrapper.

## Planned capabilities

- User accounts, isolated projects, and revocable project API keys.
- A manually instrumented Python SDK for generic operations.
- SDK telemetry ingestion and historical JSON/JSONL upload through one canonical pipeline.
- Trace and event exploration, including nested spans and a timing waterfall.
- Deterministic latency, error, token, and cost analytics with understandable anomaly insights.
- On-demand Gemini investigations that reference telemetry evidence and do not run during routine ingestion or dashboard refreshes.

JavaScript/TypeScript SDKs, automatic instrumentation, advanced OpenTelemetry integrations, distributed ingestion infrastructure, advanced alerting, and complex ML-based anomaly detection are post-MVP.

## How it is intended to work

1. A developer creates an account and project, then generates a project-scoped API key.
2. The developer instruments Python operations or uploads historical JSON/JSONL telemetry.
3. Both sources authenticate and enter the same validation, normalization, integrity-check, idempotency, and persistence pipeline.
4. The dashboard explores traces and events and presents deterministic analytics.
5. A user may explicitly request an investigation. The backend assembles a bounded evidence package, sends it to Gemini, validates the structured result, and stores the report.

Gemini is not involved in telemetry collection or routine analytics and never accesses the database directly.

## Architecture and technology

**Confirmed direction:** modular monolith; Python/FastAPI backend; Pydantic; SQLAlchemy and Alembic; PostgreSQL with JSONB; React/TypeScript/Tailwind CSS/Recharts; Python SDK; Gemini for on-demand investigations; Docker Compose for local development.

The initial database design describes eight tables: `users`, `projects`, `api_keys`, `traces`, `spans`, `events`, `uploads`, and `analysis_reports`. Architecture and detailed boundaries are proposals to validate during implementation. See [Architecture](docs/ARCHITECTURE.md), [Database Schema](docs/DATABASE_SCHEMA.md), and the [decision records](docs/decisions/).

## Repository structure

```text
README.md
AGENTS.md
CONTRIBUTING.md
docs/
  PRD.md
  ARCHITECTURE.md
  TELEMETRY_SCHEMA.md
  DATABASE_SCHEMA.md
  API_CONTRACTS.md
  INGESTION_PIPELINE.md
  SDK_SPECIFICATION.md
  FRONTEND_DESIGN.md
  MVP_SCOPE.md
  SECURITY.md
  IMPLEMENTATION_PLAN.md
  TESTING_STRATEGY.md
  DEPLOYMENT.md
  decisions/
```

## Development status

| Area | Status |
|---|---|
| Product and technical documentation | Planned foundation created in this repository |
| Backend, frontend, SDK, database, and tests | Not implemented |
| Deployment | Not implemented |

These labels describe the repository state, not a feature-completeness claim. Update them only when supported by repository evidence.

## Documentation

- Product: [PRD](docs/PRD.md), [MVP scope](docs/MVP_SCOPE.md), [implementation plan](docs/IMPLEMENTATION_PLAN.md)
- Design: [Architecture](docs/ARCHITECTURE.md), [telemetry schema](docs/TELEMETRY_SCHEMA.md), [database schema](docs/DATABASE_SCHEMA.md), [API contracts](docs/API_CONTRACTS.md), [ingestion pipeline](docs/INGESTION_PIPELINE.md), [SDK specification](docs/SDK_SPECIFICATION.md)
- Product experience and operations: [frontend design](docs/FRONTEND_DESIGN.md), [security](docs/SECURITY.md), [testing strategy](docs/TESTING_STRATEGY.md), [deployment](docs/DEPLOYMENT.md)
- Contributor guidance: [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md)
- Architecture decisions: [ADRs](docs/decisions/)

## Future roadmap

The proposed order is foundation and project security, shared telemetry ingestion, Python SDK and upload support, core trace/event UI, deterministic analytics, opt-in AI investigations, then stabilization and deployment. The roadmap assumes approximately 30 focused hours and is a prioritization aid, not a delivery guarantee. See [Implementation Plan](docs/IMPLEMENTATION_PLAN.md).
