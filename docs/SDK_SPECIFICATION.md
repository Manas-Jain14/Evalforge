# Python SDK Specification

**Status:** A Python package with manual instrumentation is **CONFIRMED**. The API below is illustrative and **PROPOSED**, not a finalized contract. Automatic instrumentation is post-MVP. The SDK never calls Gemini.

## Goals

- Make it straightforward to create a trace, nested spans, and events for generic Python work.
- Measure elapsed durations robustly and send batches to the shared ingestion pipeline.
- Keep instrumentation optional, predictable, and low overhead.
- Capture provider/model/token details only when the application supplies them.
- Avoid collecting raw prompts/responses or secrets by default.

## Illustrative usage

```python
from evalforge import EvalForge

client = EvalForge(api_key="...", environment="production")

with client.trace("customer-support-request") as trace:
    with trace.span("retrieval"):
        retrieve_documents()
    with trace.span("llm-generation") as span:
        span.set_model(provider="google", model="gemini-model")
        generate_response()
```

The import path, context-manager semantics, exception behavior, and exact methods are examples only.

## Configuration (proposed)

Inputs include project API key, endpoint/base URL, environment, service name, batch limits, flush interval, retry limits, timeout, and privacy/redaction settings. Endpoint should have a safe default for hosted EvalForge and allow local/self-hosted configuration; final host is unresolved. Secrets should be passed through a secret manager/environment, not committed source. Configuration should validate early and never log the API key.

## Lifecycle

1. Create client with key/configuration.
2. Start a trace; assign a stable UUID and capture UTC start instant plus monotonic clock baseline.
3. Start spans with optional parent determined by explicit parent or context-local active span.
4. On span completion, record end UTC and monotonic elapsed duration, status, optional exception metadata.
5. Add events at trace or span level with UTC timestamp and bounded, redacted attributes.
6. Complete trace and enqueue its telemetry.
7. Flush by batch to `/api/v1/ingest/batch`; close client deterministically.

Whether trace context managers automatically flush, and how unfinished traces are handled, are unresolved. Context managers should reliably close span timing when exceptions occur and record a sanitized error without suppressing the application's exception by default.

## Nested/context propagation

Context-local state is proposed for synchronous nesting and should not leak across concurrent tasks. Async APIs should preserve context across `asyncio` task boundaries. Cross-thread and process propagation are not promised in MVP; provide explicit parent/context handoff rather than unsafe global mutable state. A trace context serialization format is unresolved.

## Metadata, events, and errors

Generic span names/types are supported. Provider, model, token counts, and other specialized values are optional. SDK should not estimate authoritative costs; server-side configured pricing produces reported cost. Unknown model pricing remains unavailable.

Events support error, retry, warning, custom event, and milestone semantics without a rigid event-type enum. Exceptions should be captured as type and safe message only under redaction rules; stack traces and exception locals may expose secrets and are off by default.

## Batching, flush, retries, and idempotency

Buffer completed records up to bounded count/byte size and optionally an interval; flush explicitly and on close. Use bounded network timeouts and retry transient failures with capped exponential backoff and jitter. Do not retry permanent validation/auth errors indefinitely. Batch ID and stable record IDs enable safe retries; exact server idempotency contract must match [Ingestion Pipeline](INGESTION_PIPELINE.md).

**UNRESOLVED:** default buffer limits, flush interval, retry count, disk spooling, and behavior after unrecoverable flush failure. MVP should avoid unbounded memory or silent data loss; expose errors/status and document shutdown flushing. No background worker is required unless needed by measured use cases.

## Network and application impact

Instrumentation must never invoke an LLM. Network send should not block each instrumented operation beyond explicitly synchronous use; choose flush strategy after measuring. Provide explicit `flush()` and `close()` with observable failures. Decide whether telemetry network failures can propagate on explicit flush while never masking user exceptions from a context manager.

## Sensitive-data handling

Raw prompts, completions, credentials, headers, and request bodies are not captured by default. Allow explicit opt-in and redaction controls for attributes/messages. The SDK should have conservative attribute size/depth bounds and avoid logging payloads. Server investigation consent and transfer policy remain authoritative. See [Security](SECURITY.md).

## Compatibility, packaging, testing

Supported Python versions, sync/async public API, package name/versioning, and transport dependency are unresolved. Pin no speculative compatibility promise. Tests should cover normal and exceptional lifecycle, nesting/concurrency context, monotonic duration, serialization, redaction, bounded buffering, retry classification, idempotent replay, and shutdown behavior. Use pytest.
