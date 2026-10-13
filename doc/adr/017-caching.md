# ADR-017: No Response Caching

## Status

Accepted

Adapts the platform's [ADR-018: Caching](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/018-caching.rst).

## Context

The platform caches function results server-side (ADR-018). The prototype SDK kept an in-process cache of resources, which served stale data after a change made elsewhere, e.g. by the cli.

## Decision

The SDK doesn't cache responses. Every call reads the platform's current state. Callers who need a cache add one with their own invalidation rules. (The only cache is of Pydantic type adapters, which are code, not data.)

## Alternatives Considered

- An LRU cache of resources, as the prototype had.

## Consequences

- **Positive:**
  - No stale reads, and no cache invalidation in the SDK.
- **Negative:**
  - Repeated reads cost a request each.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-008: HTTP Transport, Retries and Timeouts](008-http-transport.md)
