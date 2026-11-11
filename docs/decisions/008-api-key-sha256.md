# ADR 008: SHA-256 verification for project API keys

- **Status:** Accepted
- **Date:** 2026-11-11

## Context

Project API keys are generated with high entropy and are used as bearer credentials for telemetry ingestion. The Phase 1 password hasher is intentionally slow and designed for human-selected passwords, not randomly generated API secrets. API key records need a non-secret lookup identifier, display-only prefix, and verification value; the full secret must never be recoverable from storage or returned after creation.

## Decision

- Generate a URL-safe API key secret containing at least 32 bytes of cryptographic randomness.
- Persist only the lowercase hexadecimal SHA-256 digest of the complete secret, along with a separate non-secret key ID and display prefix.
- Resolve an API key by its key ID, then compare the supplied secret's SHA-256 digest with the stored digest using a constant-time comparison.
- Do not use the password hasher for API keys. Return the complete secret only in the successful creation response.

## Consequences

- The API key secret cannot be retrieved from the database after creation; clients must securely retain it.
- SHA-256 is appropriate here because the generated secret has high entropy; unlike passwords, it does not need a deliberately slow password KDF.
- Key rotation is performed by creating a new key and revoking the old one.
- A future decision may add a keyed digest or a key-version field if operational requirements justify pepper rotation.
