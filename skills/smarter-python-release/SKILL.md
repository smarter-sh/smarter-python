---
name: smarter-python-release
description: Use when working on smarter-python's CI/CD, dependencies or releases - the requirements files (requirements/in/constraints.in, base.in, local.in, compiled by make python-requirements), pyproject.toml and its hatchling build, the CI workflow (lint, the Python test matrix, docs, terraform, build), Codecov, semantic-release (release.config.js, versions, the changelog, tags, prereleases from alpha and beta), the Release workflow and PyPI trusted publishing of smarter-api, and supported Python versions - or when asked why CI failed, what the next version will be, or how to cut a release.
---

# smarter-python CI/CD and Releases

smarter-python's CI and releases are laid out exactly as cache-results'
(`../cache-results`, skill `cache-results-release`), the model for every Smarter
PyPI project. When you change one, consider whether the other should follow.

## CI (`.github/workflows/ci.yml`)

Runs on every pull request, and as the first job of every Release run, which
starts on every push to `main`, `alpha` and `beta`:

| Job         | What it does                                                                               |
| ----------- | ------------------------------------------------------------------------------------------ |
| `lint`      | `pre-commit run --all-files`: the same hooks as `make lint`                                |
| `test`      | `coverage run -m unittest discover -s tests -t .` on Python 3.10 to 3.14                   |
| `docs`      | `sphinx-build -W --keep-going`: the docs site, warnings as errors (`make sphinx-build`)    |
| `terraform` | `fmt -check`, `init -backend=false` and `validate` of `terraform/docs`, with no AWS access |
| `build`     | after the others: `python -m build`, `twine check --strict`, the `dist` artifact           |

Every `make` target has a CI counterpart, and the other way round: keep them
consistent when you change either.

```console
gh run list --limit 5
gh run view <id>            # jobs and annotations
gh run view <id> --log-failed
```

- CI installs the package with `pip install -e ".[test]"`, not
  `requirements/local.txt`, so that it tests what users install.
- The unit tests never reach a platform, and the live tests skip: CI never
  sets `SMARTER_TEST_LIVE`.
- Each test job uploads `coverage.xml` to **Codecov** (`codecov.yml`: 95%
  project and patch targets), flagged `python`. Codecov merges them. The upload
  needs the repository secret `CODECOV_TOKEN`, and never fails CI.
  `[tool.coverage]` in `pyproject.toml` measures branches and fails below 95%.
- Action versions are pinned to a major (`actions/checkout@v7`). Look up the
  latest with `gh api repos/<owner>/<action>/releases/latest --jq .tag_name`
  rather than from memory.
- Lint workflows with actionlint before committing:
  `docker run --rm -v "$(pwd)":/repo --workdir /repo rhysd/actionlint:latest`.

## Packaging (`pyproject.toml`)

- Built by **hatchling**. The version is read from `smarter/__version__.py`.
  The wheel holds `smarter/` only (with `py.typed`); the sdist adds `tests/`,
  `README.md`, `LICENSE.txt` and `CHANGELOG.md`. Include patterns start with
  `/`: without it, hatch matches every nested `README.md`.
- `authors` is The Smarter Project, and Lawrence McDaniel is the maintainer.
- The runtime dependencies are compatible ranges, not pins: an application
  that installs the SDK pins its own versions.
- Extras: `test` (what CI's test jobs need) and `docs` (what the docs job needs).

## Versions come from commits: semantic-release

`release.config.js` configures semantic-release. From the conventional
commits since the last tag (`smarter-git-commits`):

- `fix` and `perf` make a patch release, `feat` a minor one, a
  `BREAKING CHANGE:` footer a major one. Other types make none.
- It writes the version into `smarter/__version__.py`, updates
  `CHANGELOG.md`, commits both as `chore(release): <version> [skip ci]`, tags
  `v<version>`, and publishes a GitHub release.
- **Never edit `__version__.py` or `CHANGELOG.md` by hand**, and never write a
  `chore(release)` commit.
- `main` makes releases. `alpha` and `beta` make prereleases, e.g.
  `0.6.0-alpha.1`, which Python's packaging normalizes to `0.6.0a1`.

## The Release workflow (`.github/workflows/release.yml`)

Runs on **every push to `main`, `alpha` and `beta`**: a push to `main` makes a
release, and a push to `alpha` or `beta` a prerelease. A push whose commits
since the last tag release nothing (`docs`, `ci`, `build`, `chore`, ...) runs CI
and stops. semantic-release's own commit ends in `[skip ci]`, so it starts no
run. Runs are one at a time per branch: a push during a release waits, then
releases everything since the last tag. It can also be started by hand:

```console
make release-dry-run     # gh workflow run release.yml -f dry_run=true: CI, then the next version
make release             # the same as a push, e.g. to re-run a release
make release RELEASE_BRANCH=alpha   # a prerelease, to TestPyPI only
gh run watch
```

1. `ci`: the whole CI workflow (`ci.yml` is also a reusable workflow). Nothing
   is released unless it passes.
2. `release`: semantic-release, as above. A dry run stops here, and the run's
   summary shows the last and next versions.
3. `dist`: checks out the new tag, builds, `twine check --strict`, and fails
   unless `__version__.py` is the release, and `dist/` holds exactly one wheel
   and one sdist of it, named with the PEP 440 spelling
   (`smarter_api-0.6.0a1-py3-none-any.whl`).
4. `attach`: uploads the distributions to the GitHub release.
5. `publish-testpypi`, then `verify-testpypi`: a rehearsal on TestPyPI, when
   the variable `PUBLISH_TO_TESTPYPI` is `"true"`. The verify job installs the
   upload back, its dependencies from PyPI and only smarter-api from TestPyPI
   (anyone can upload a look-alike of a dependency there), and checks the
   installed `smarter.__version__`. Keep its list of dependencies the same as
   `pyproject.toml`'s.
6. `publish-pypi`, then `verify-pypi`: PyPI, **from `main` only**, when
   `PUBLISH_TO_PYPI` is `"true"`, and only if the rehearsal passed or is off.
   Prereleases from `alpha` and `beta` stop at TestPyPI.

- Releasing and publishing are **one workflow**, so that a tagged release
  can't miss PyPI. There is no `make publish-*` and no `twine upload`.
- Uploads use **trusted publishing** (OIDC): there is no PyPI token anywhere.
  Each index needs `release.yml` registered as a trusted publisher of the
  `smarter-api` project, for the `testpypi` and `pypi` environments.
- Uploads `skip-existing`, so a run that failed after an upload can be run
  again.

- The README's and docs' status badge is the Release workflow's, on `main`:
  `ci.yml` runs on pushes only inside it.

Secrets: `CODECOV_TOKEN` (coverage), and `PAT` only when `main` is protected
against `GITHUB_TOKEN`'s pushes. Variables: `PUBLISH_TO_TESTPYPI` and
`PUBLISH_TO_PYPI`, `"false"` until the trusted publishers are registered.

## Dependencies and requirements

Laid out as cache-results' and Smarter's:

| File                                 | What it holds                                                          |
| ------------------------------------ | ---------------------------------------------------------------------- |
| `pyproject.toml`                     | What the **published** package needs, as compatible ranges             |
| `requirements/in/constraints.in`     | Global version constraints, with a reason each. Every `.in` uses `-c`  |
| `requirements/in/base.in`            | The runtime requirements, unpinned                                     |
| `requirements/in/local.in`           | Every developer tool, unpinned and commented                           |
| `requirements/base.txt`, `local.txt` | **Generated** by pip-compile: every version pinned. Never edit by hand |

```console
make python-requirements   # pip-compile --upgrade both .in files, then install local.txt and the package
make init                  # rebuild venv/ from local.txt, install the package editable, and the git hooks
```

- `.in` files include constraints with `-c constraints.in`, not `-r`: a
  constraint limits a version but never adds a package, so `base.txt` holds
  only the runtime dependencies.
- A new development tool goes into `in/local.in`, with a comment saying what
  it is for, then `make python-requirements`. A new runtime dependency is a
  decision: it goes into `pyproject.toml` **and** `in/base.in`, with the same
  range in `constraints.in`, and into the `verify-testpypi` job's install.
- `datamodel-code-generator` is pinned in `constraints.in`: it generated
  `smarter/models/sam/`, and a new version can change every generated file.
  Upgrade it together with `make sam-models`.
- `--no-strip-extras` keeps `coverage[toml]`'s extra in `local.txt`.
- The compiled files are committed, as a `build(deps):` commit.

## Supported versions

Python 3.10 and newer (ADR-019). When a Python release arrives or reaches end
of life, change together: the `ci.yml` matrix, the `pyproject.toml`
classifiers (and `requires-python`), the README's badge, and `CLAUDE.md`.
Dropping a version is a breaking change.
