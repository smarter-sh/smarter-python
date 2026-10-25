ADR-018: A Synchronous Client First
===================================

Status
------

Accepted

Context
-------

Python programs are synchronous or ``asyncio``-based. The ``openai`` package offers both clients. Two clients double the code to maintain and test.

Decision
--------

The SDK offers a synchronous client, ``smarter.Smarter``. The transport is ``httpx``, which has an async counterpart, and the resources build their requests in one place, so that an ``AsyncSmarter`` can be added without changing the public api. Until then, async applications call the SDK in a thread (``asyncio.to_thread``).

Alternatives Considered
-----------------------

- Both clients from the start.
- An async client only.

Consequences
------------

- **Positive:**

  - One client to maintain while the api coverage grows.

- **Negative:**

  - Async applications pay for a thread per concurrent call.

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-008: HTTP Transport, Retries and Timeouts <008-http-transport>`
