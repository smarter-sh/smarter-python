# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

smarter-python is the Smarter platform's official Python SDK, published to PyPI
as `smarter-api`, with the import name `smarter`. It is to the Smarter platform
([smarter-sh/smarter](https://github.com/smarter-sh/smarter), usually checked
out beside this repository as `../smarter`) what the `openai` package is to the
OpenAI api: the library that Python programmers import to build software on
their own Smarter installation, without customizing or forking the platform.
The [smarter cli](https://github.com/smarter-sh/smarter-cli) covers the same api
for people at a terminal.

Detailed know-how lives in the Agent Skills under `skills/` (symlinked to
`.claude/skills`). **Load `smarter-python-development` first for any change.**
This file holds only what applies to nearly every task.

## Hard rules

1. **Never run git write commands**, here or in `../smarter`. "Write a git
   commit" means print the command as text. See `smarter-git-commits`.
2. **Run the tests yourself** after any change (`make test`), and the live
   tests against the local platform when you change a model or an endpoint.
   Never ask the user to re-run them. Report failures honestly.
3. **Never deploy from a test or a probe.** Deploy creates real, billable
   infrastructure. The local platform's containers hold live credentials.
4. **The pre-commit hooks are the lint standard.** See `smarter-code-quality`.
5. **Coverage:** at least 95%, with branch coverage. CI fails below it.
6. **This repository is public.** No api keys, tokens, account numbers,
   private hostnames, names or customer data in code, fixtures, docs or skills.
7. **`PYTHONPATH` is the repository root, never `./smarter`**, which would
   shadow the standard library.
8. **Live prompt calls are fine.** Live tests and probes send billable LLM
   prompts; that is accepted.

## Repository map

| Path                 | Contents                                                                                                 |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| `smarter/client.py`  | `Smarter`, the client                                                                                    |
| `smarter/core/`      | Configuration, http transport, exceptions, logging, SSE, type aliases                                    |
| `smarter/resources/` | One module per resource family                                                                           |
| `smarter/models/`    | Pydantic models; `sam/` is generated, `chat.py`/`journal.py`/`react.py` mirror the platform's contracts  |
| `scripts/`           | SAM model generation, contract sync                                                                      |
| `tests/`             | Unit tests, fixtures in `tests/data/`, live tests in `tests/live/`                                       |
| `docs/source/`       | The Sphinx site, https://docs.smarter-python.smarter.sh/; `adr/` holds the architecture decision records |
| `terraform/docs/`    | The docs site's AWS resources                                                                            |
| `.github/workflows/` | `ci.yml` (every push and pull request) and `release.yml` (by hand: CI, release, TestPyPI, PyPI)          |
| `skills/`            | Agent Skills                                                                                             |

The SDK's documentation is its own site, built from `docs/source/` and
published to https://docs.smarter-python.smarter.sh/. CI, Codecov and releases
follow cache-results (`../cache-results`), the model for every Smarter PyPI
project.

## Common commands

```bash
make test                                   # unit tests
make coverage                               # unit tests with coverage
SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=... make test-live
make sam-models                             # make contracts, then regenerate smarter/models/sam
make contracts                              # copy the platform's contracts, SAM schemas and openapi.json from ../smarter
make sphinx-build                           # the docs site, warnings as errors (seconds)
make release-dry-run                        # CI, then the next version, without releasing
git diff --name-only | xargs venv/bin/pre-commit run --files
```

Monthly, sync the SDK with the platform and update its requirements: load the
`monthly-maintenance` skill.

## Definition of done

- The change follows an existing pattern, and the ADRs in `docs/source/adr/`.
- Tests cover it, you ran them, and the live tests pass or skip only for named platform bugs.
- Pre-commit hooks pass on the changed files.
- Public objects have reST docstrings; user-facing features are documented in `docs/source/`.
- Your summary says what changed, what you verified, what you skipped, and any platform bugs found.
