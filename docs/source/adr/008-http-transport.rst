ADR-008: HTTP Transport, Retries and Timeouts
=============================================

Status
------

Accepted

Context
-------

Requests fail for transient reasons: timeouts, rate limits, gateways. The platform also answers 503 for a resource that isn't ready (``SAMBrokerErrorNotReady``), which no retry will fix. A prompt that calls several tools can take tens of seconds.

Decision
--------

All requests go through one transport, ``smarter.core.http.SmarterHttpClient``, on ``httpx``. It retries a request that got no response, or a 408, 429, 502 or 504, and a 503 only when the platform didn't send it (its body is not a journaled response), with exponential backoff and jitter, honoring ``Retry-After`` up to 60 seconds. The default is 2 retries and a 60 second timeout. Callers may pass their own ``httpx.Client``, which the SDK never closes. Prompt progress is read as Server-Sent Events by the SDK's own parser.

Alternatives Considered
-----------------------

- ``requests``, which has no streaming of Server-Sent Events comparable to ``httpx``'s, and no async counterpart for a future async client.
- No retries.

Consequences
------------

- **Positive:**

  - Transient failures are absorbed, and semantic ones fail fast.

- **Negative:**

  - A retried prompt may be billed twice if the first attempt reached the LLM. ``max_retries=0`` disables retries where that matters.

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-006: Error Handling <006-error-handling>`
- :doc:`ADR-018: A Synchronous Client First <018-synchronous-client>`
