ADR-009: Testing
================

Status
------

Accepted

Adapts the platform's `ADR-013: Testing <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/013-testing.rst>`__.

Context
-------

The SDK's correctness depends on a platform that it can't run in CI, and the local platform's containers hold credentials for real cloud infrastructure.

Decision
--------

There are two suites:

- **Unit tests** (``tests/test_*.py``, one per source module) subclass ``tests.base.SmarterTestBase``, the SDK's counterpart of the platform's base class. An ``httpx.MockTransport`` answers every request with sanitized copies of real platform responses (``tests/data/``). They run in CI on every supported Python version, with at least 90% coverage.
- **Live tests** (``tests/live/``, skipped unless ``SMARTER_TEST_LIVE=true``) run against a real platform, and validate every model against real responses. They may send billable prompts, and create and delete throwaway resources. **They never deploy anything.** A platform error skips a subtest with the platform's message, and an SDK error fails it.

Alternatives Considered
-----------------------

- Only mocked tests. Models would describe what their author guessed.
- Only live tests. CI would need a platform.

Consequences
------------

- **Positive:**

  - Fast, hermetic CI, and models checked against reality before release.

- **Negative:**

  - Live tests must be run by hand before a release.

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-005: Mirrored Contracts and Generated SAM Models <005-platform-models>`
- :doc:`ADR-010: CI/CD <010-ci-cd>`
- :doc:`ADR-016: Security <016-security>`
