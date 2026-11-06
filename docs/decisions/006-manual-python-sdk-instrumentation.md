# ADR 006: Start with manual Python SDK instrumentation

- **Status:** Accepted (Python-first/manual-instrumentation MVP confirmed)
- **Date:** 2026-11-06

## Context

The initial product focuses on Python and has a limited delivery window. Automatic integrations increase compatibility and debugging scope.

## Decision

Build a Python package for manual trace, span, event, and error instrumentation. Keep provider/model/token metadata optional and support generic operations. Automatic instrumentation and JavaScript/TypeScript SDKs are post-MVP.

## Consequences

- Small, explicit API surface can be tested and documented.
- Developers decide where instrumentation boundaries occur.
- Context propagation, async/thread semantics, flushing, retry limits, and package compatibility need finalization.
- SDK never calls Gemini and should have bounded overhead and safe privacy defaults.

## Revisit when

The manual API is stable and real user demand justifies a specific supported integration. Automatic instrumentation must not compromise existing manual behavior.
