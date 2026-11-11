# Instructions for AI coding agents

## Project status and architecture

EvalForge has a Phase 1 FastAPI backend foundation for authentication and owner-scoped projects. Telemetry ingestion, SDK, analytics, investigations, and frontend remain planned. The intended product is a Python-first LLM observability and investigation platform using a modular monolith: one FastAPI backend, PostgreSQL, a React/TypeScript frontend, a manually instrumented Python SDK, deterministic analytics, and explicitly requested Gemini investigations. Read the relevant docs before implementing anything; proposals in the docs are not automatically approved implementation facts.

Start with [Architecture](docs/ARCHITECTURE.md), then consult the focused schema, API, ingestion, SDK, design, security, testing, and deployment documents. ADR status is explicit in [docs/decisions](docs/decisions/).

## Working rules

- Inspect the current branch, worktree, relevant files, and existing patterns before changing code.
- Prefer small, focused changes. Do not rewrite unrelated modules or create application boilerplate unless requested.
- Keep FastAPI domains modular within the monolith. Do not add microservices, Kafka, Redis, Celery, Kubernetes, or similar infrastructure without a concrete approved need.
- Use Pydantic for boundary validation, SQLAlchemy for persistence, and Alembic for schema evolution when those layers are implemented.
- Preserve project ownership and isolation in every user-facing data path. Resolve SDK project identity from the authenticated API key, never from a client-supplied project ID.
- Treat user input and uploaded telemetry as untrusted. Do not bypass validation, authorization, privacy controls, or idempotency.
- Do not store plaintext API keys or hardcode secrets. Follow [Security](docs/SECURITY.md); use placeholder-only examples.
- Keep provider/model/token metadata optional for generic spans. Use UTC timestamps and monotonic clocks for SDK elapsed durations.
- Gemini is only for explicit investigations. Do not route ingestion, SDK collection, or deterministic analytics through an LLM.
- Add focused tests for meaningful behavior and run the narrowest relevant checks, then report their actual results. Never invent test outcomes.
- Do not introduce dependencies or change architectural decisions without explaining the need and updating relevant documentation.
- Do not use fake production telemetry or commit credentials, private prompts, or customer data.
- Update directly related documentation when behavior, contracts, schema, security, or developer workflows change.

## Current backend organization

The Phase 1 backend lives under `backend/app`: API routes, core configuration/security/dependencies, SQLAlchemy DB/models, Pydantic schemas, and domain services. Keep route handlers thin and extend these patterns only for implemented domains. Future frontend pages should be organized around product workflows and reusable design-system elements; the Python SDK should remain separate from the server.

## Database and migrations

- Schema changes require Alembic migrations; do not rely on implicit production schema creation.
- Preserve foreign-key integrity, project scoping, nonnegative duration/token constraints, and appropriate indexes.
- Prefer composite relationships where they prevent cross-project trace/span/event links.
- Review migration upgrade and downgrade behavior and test it against PostgreSQL.
- Do not mutate historical migration files after they have been applied in shared environments.

## Testing

Use pytest for backend and SDK tests. Add frontend tests using a tool selected when frontend implementation begins. Cover authorization boundaries, malformed/oversized payloads, SDK lifecycle and flush behavior, ingestion idempotency, analytics definitions, evidence grounding, and light/dark theme accessibility. Follow [Testing Strategy](docs/TESTING_STRATEGY.md).

## Environment and secrets

Read configuration from environment variables, validate required settings at startup, and document names and safe placeholders. Do not create or commit a real `.env`; do not print secret values in logs, errors, tests, or examples. See [Deployment](docs/DEPLOYMENT.md) and [Security](docs/SECURITY.md).

## Documentation and decision changes

Use the status labels **CONFIRMED**, **PROPOSED**, and **UNRESOLVED** accurately. Update all affected cross-document contracts together. If existing implementation conflicts with documentation, report the conflict and seek a decision rather than silently replacing either. Mermaid diagrams should render; links should be relative and checked.

## Git safety

- Never change branches, stage, commit, push, or create a pull request unless explicitly asked.
- Never discard or overwrite user changes. Inspect before editing.
- Do not run destructive commands or delete unrelated files.
- Summarize changed files, validation performed, and any unresolved issues.
