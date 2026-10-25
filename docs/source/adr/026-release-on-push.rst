ADR-026: Release on Every Push
==============================

Status
------
Accepted

Supersedes the part of :doc:`ADR-024: CI and the Release Workflow <024-release-workflow>` that starts releases by hand.

Context
-------
A release that waits for someone to start it is a release that is forgotten:
fixes merge into ``main`` and sit unpublished, and nobody can tell from the
repository whether a commit has reached PyPI. The conventional commits already
say whether a change deserves a release, so the decision needs no person.

Decision
--------
``release.yml`` runs on every push to ``main``, ``alpha`` and ``beta``, and can
still be started by hand (``make release-dry-run``, ``make release``). It runs
the whole of ``ci.yml`` first, then semantic-release, which releases only when
the commits since the last tag include a ``fix``, ``perf``, ``feat`` or breaking
change. ``main`` publishes to PyPI, and ``alpha`` and ``beta`` publish
prereleases to TestPyPI. ``ci.yml`` runs on its own only for pull requests, so
each push is tested once, and the status badge is the Release workflow's.
Releases run one at a time per branch.

Alternatives Considered
-----------------------
- Releases started by hand, which leave merged fixes unpublished.
- Release on a schedule, which delays every fix and still releases unreviewed batches.
- Run ``ci.yml`` on pushes as well, which tests every push twice.

Consequences
------------
- **Positive:**

  - Every ``fix`` or ``feat`` that reaches ``main`` is on PyPI minutes later.
  - Whether a commit is released is decided by its message, in review.

- **Negative:**

  - A commit's type matters: a ``fix`` merged by mistake is published.
  - A push to ``alpha`` or ``beta`` with a ``fix`` or ``feat`` uploads a prerelease to TestPyPI.

Related ADRs
------------
- :doc:`ADR-024: CI and the Release Workflow <024-release-workflow>`
- :doc:`ADR-015: Semantic Versioning and API Versions <015-versioning>`
