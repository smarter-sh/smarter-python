ADR-007: Logging
================

Status
------

Accepted

Adapts the platform's `ADR-011: Logging <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/011-logging.rst>`__.

Context
-------

The platform controls its logging per module with waffle switches (ADR-011). A library has no waffle switches, must not configure its caller's logging, and must never log an api key.

Decision
--------

The SDK logs to the standard library's ``smarter.*`` logger hierarchy (``smarter.client``, ...), which gives the per-module control that ADR-011 asks for. It adds no handlers, unless ``SMARTER_LOG=info`` (requests: method, url, status, duration) or ``SMARTER_LOG=debug`` (and their bodies) asks it to. Api keys are masked by ``mask_secret()`` everywhere they appear.

Alternatives Considered
-----------------------

- Waffle-like switches of the SDK's own.
- Configure a handler at import.

Consequences
------------

- **Positive:**

  - The SDK behaves as a well-mannered library.
  - Debugging a request needs only an environment variable.

- **Negative:**

  - Debug logs contain request bodies, e.g. prompts, which the caller must treat as sensitive.

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-016: Security <016-security>`
