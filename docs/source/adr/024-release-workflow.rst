ADR-024: CI and the Release Workflow
====================================

Status
------

Accepted

Supersedes :doc:`ADR-010 <010-ci-cd>`.

Context
-------

Every change must be linted, tested and buildable before it is released, and a release must reach PyPI the moment it is tagged. When publishing was a separate step, done by hand from one person's machine, the SDK's GitHub releases ran several versions ahead of PyPI.

Decision
--------

CI/CD uses GitHub Actions, in two workflows, and every ``make`` target has a CI counterpart.

- ``ci.yml`` runs on every push to ``main``, ``alpha`` and ``beta``, and on every pull request: the pre-commit hooks, the unit tests with coverage on every supported Python version (:doc:`ADR-019 <019-python-versions>`), the Sphinx build with warnings as errors, a check of the docs site's Terraform, and then a build of the sdist and wheel, checked with ``twine check --strict``. Coverage, with branches, is uploaded to Codecov, which checks 95% of the project and of each patch, and CI fails below 95%.
- ``release.yml`` is started by hand, and releases and publishes in one run: the whole of ``ci.yml``, semantic-release (:doc:`ADR-015 <015-versioning>`), a build from the new tag that must hold exactly that version, the distributions attached to the GitHub release, a rehearsal upload to TestPyPI that is installed back and checked, and then PyPI, from ``main`` only, also installed back and checked. Prereleases from ``alpha`` and ``beta`` stop at TestPyPI.
- Uploads use trusted publishing (OIDC), with no stored PyPI token, and are switched on by the repository variables ``PUBLISH_TO_TESTPYPI`` and ``PUBLISH_TO_PYPI``.

Alternatives Considered
-----------------------

- Release on every push to ``main``, which releases every merged fix before they can be reviewed together.
- Publish to PyPI by hand after the release, which lets a tagged release never reach PyPI.
- Publish with a PyPI api token stored as a secret, which can leak and must be rotated.

Consequences
------------

- **Positive:**

  - A tagged release is on PyPI, or the run that tagged it failed visibly.
  - The same workflows as the other Smarter Project packages.

- **Negative:**

  - Releases need someone to start them.
  - Each package index needs ``release.yml`` registered as a trusted publisher.

Related ADRs
------------

- :doc:`ADR-009: Testing <009-testing>`
- :doc:`ADR-015: Semantic Versioning and API Versions <015-versioning>`
- :doc:`ADR-023: A Documentation Site of Its Own <023-documentation-site>`
- :doc:`ADR-025: Packaging and Compiled Requirements <025-packaging>`
- `Smarter ADR-014: CI CD <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/014-ci-cd.rst>`__
