# Contributing

EvalForge has a Phase 1 backend foundation for authentication and project management; the rest of the product is planned. Contributions should extend the small, secure, end-to-end Python-first MVP without obscuring what is implemented versus planned.

## Before changing anything

1. Read [AGENTS.md](AGENTS.md) and the relevant documents under [docs](docs/).
2. Inspect the worktree and existing conventions; preserve unrelated changes.
3. Confirm whether a proposed behavior is **CONFIRMED**, **PROPOSED**, or **UNRESOLVED**. Ask before resolving consequential open decisions.
4. Prefer a demonstrable end-to-end slice over unrelated scaffolding.

## Engineering expectations

- Keep the backend a modular monolith and reuse the shared telemetry pipeline for SDK and historical uploads.
- Enforce project isolation at query and relationship boundaries; never accept SDK project identity as authorization.
- Validate inputs, bound request sizes, and return consistent errors without exposing secrets.
- Use migrations for schema changes. Keep timestamps UTC, elapsed duration monotonic at the SDK boundary, and generic span metadata optional.
- Keep analytics deterministic and independent of Gemini. Only user-initiated investigations may call Gemini, with privacy controls and evidence references.
- Avoid unnecessary infrastructure and dependencies. Automatic instrumentation and non-Python SDKs are outside the MVP.

## Tests and documentation

Add focused tests for changed behavior and run the narrowest applicable suite. Include security and failure-path tests where relevant. Report commands and outcomes accurately. Update the API, schema, security, SDK, frontend, or deployment documentation affected by a change; keep status labels honest.

## Pull request description checklist

- State the problem and the smallest complete change.
- List affected contracts, migration implications, and security/privacy considerations.
- List tests run and actual results; identify checks not run.
- Call out unresolved decisions and any change to an ADR.
- Do not include real credentials, customer telemetry, or raw sensitive prompts.

Do not stage, commit, push, or create a pull request unless the task explicitly requests it.
