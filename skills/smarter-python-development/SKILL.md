---
name: smarter-python-development
description: Start here for any change to the smarter-python repository, the Smarter platform's Python SDK (the smarter-api PyPI package). Gives the non-negotiable rules, the SDK's architecture (client, transport, resources, models, the generated SAM models and the mirrored api contracts), how to cover a new platform endpoint, and an index of the narrower skills to load for each kind of work.
---

# Smarter Python SDK Development

`smarter-api` (import name `smarter`) is to the Smarter platform what the
`openai` package is to the OpenAI api: the library that Python programmers
import to build custom software on their own Smarter installation, running
locally or on Kubernetes. The platform itself is
[smarter-sh/smarter](https://github.com/smarter-sh/smarter), usually checked out
beside this repository as `../smarter`. The
[smarter cli](https://github.com/smarter-sh/smarter-cli) covers the same api for
people at a terminal.

The SDK's goal is to cover **all** of the platform's api, so that nobody needs
to customize or fork the backend to integrate with it.

The **minimum** is everything needed to work with Smarter manifests the way the
platform does: every broker verb, and the enumerations that the brokers are
built on. Those enumerations are never copied from the platform. They live in
[smarter-types](https://github.com/smarter-sh/smarter-types) (`../smarter-types`,
import `smarter_types`), which the platform and the SDK both depend on, and the
SDK re-exports them (e.g. `SAMKinds` in `smarter/models/kinds.py`). When
platform code that handles manifests relies on a plain-Python enum or helper
that the SDK lacks, move it into smarter-types and re-export it from both. Beyond that, the SDK should let a program do the administrative
tasks that are otherwise done in Django Admin or with `manage.py`, as the
platform exposes them through its api.

## Repository map

| Path                                               | What lives there                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `smarter/client.py`                                | `Smarter`, the client: configuration, the resources, `whoami`/`version`/`status`     |
| `smarter/core/conf.py`                             | `SmarterSettings` and the configuration lookup (arguments, env, cli config file)     |
| `smarter/core/http.py`                             | `SmarterHttpClient`: auth, retries, error mapping, response validation, SSE          |
| `smarter/core/exceptions.py`                       | The exception hierarchy. Every exception is a `SmarterError` (ADR-012)               |
| `smarter/resources/`                               | One module per resource family: `llmclients.py`, `guardrails.py`, ...                |
| `smarter/models/`                                  | Pydantic models of the api's responses, one module per family                        |
| `smarter/models/chat.py`, `journal.py`, `react.py` | Mirrors of the platform's api contracts                                              |
| `smarter/models/sam/`                              | **Generated** SAM models of every manifest kind. Never edit by hand                  |
| `scripts/`                                         | `generate_sam_models.py`, `sync-contracts.sh`                                        |
| `tests/`                                           | Unit tests (`tests/test_*.py`), fixtures (`tests/data/`), live tests (`tests/live/`) |
| `docs/source/`                                     | The Sphinx site, https://docs.smarter-python.smarter.sh/, and its api reference      |
| `docs/source/adr/`                                 | The SDK's architecture decision records, which adapt the platform's                  |
| `terraform/docs/`                                  | The docs site's AWS resources (S3, CloudFront, ACM, Route53)                         |
| `requirements/in/`                                 | The `.in` files that pip-compile pins into `requirements/*.txt`                      |
| `.github/workflows/`                               | `ci.yml` (pull requests) and `release.yml` (every push: CI, then release)            |
| `skills/`                                          | These skills                                                                         |

The SDK has its own documentation site, built from `docs/source/` and
published to https://docs.smarter-python.smarter.sh/. Every page's footer says
it is part of The Smarter Project. The platform's docs keep one short page,
`../smarter/docs/source/smarter-framework/smarter-python.rst`, that links to
it. See `smarter-sphinx-docs`.

## Non-negotiable rules

1. **Never execute git write commands**, in this repository or in `../smarter`.
   "Write a git commit" means output the command text. See `smarter-git-commits`.
2. **Run the tests yourself**, after every change: `make test` (or the
   command in `smarter-python-testing`). Never ask the user to re-run them.
   Report failures honestly, including pre-existing ones.
3. **Validate against a real platform.** A model that has only met a
   hand-written fixture is a guess. Probe the endpoint (`smarter-api-testing`),
   build sanitized fixtures from real responses, and run `make test-live`
   against the local platform before you call an endpoint covered.
4. **Never deploy from a test.** `deploy` creates real, billable cloud
   infrastructure (DNS, certificates, Kubernetes ingresses, GPU nodes). The live
   tests never call it. The local platform's containers hold live credentials:
   see `smarter-infrastructure-safety` in `../smarter/skills/`.
5. **The pre-commit hooks are the lint standard.** See `smarter-code-quality`.
6. **Coverage:** at least 95%, with branch coverage. `make coverage` and CI
   fail below it, and Codecov checks each pull request's patch.
7. **This repository is public.** No api keys, tokens, account numbers,
   private hostnames, names, addresses or customer data in code, fixtures,
   docs or skills. Sanitize every fixture taken from a real response, and
   grep it before you finish.
8. **Never run with `./smarter` on `PYTHONPATH`.** The package's own directory
   on the path shadows the standard library (`types`, `typing`, `http`).
   `PYTHONPATH` is the repository root, or unset.
9. **Pydantic over JSON (ADR-031).** Every response is a model. No
   `list[Any]` or `dict[str, Any]`: arbitrary JSON is `SmarterJsonType`
   (`pydantic.JsonValue`), and a JSON object whose shape depends on a kind is
   `SmarterJsonObjectType`. See `smarter-python-typing`.
10. **Docstrings are reStructuredText** (`:param:`, `:returns:`, `:raises:`),
    exactly as in the platform. See `smarter-docstrings`.
11. **Type annotations are required** for every public function and method,
    and for every attribute of a Pydantic model. See `smarter-python-typing`.
12. **CI and releases follow cache-results**, the model for every Smarter
    PyPI project: `ci.yml` on every pull request, and `release.yml` on every
    push to `main`, `alpha` and `beta`, which runs CI, versions with
    semantic-release, and publishes to TestPyPI and PyPI by trusted
    publishing. Every `make` target has a CI
    counterpart. See `smarter-python-release`.
13. **The docs site is this repository's own** (`docs/source/`), built with
    warnings as errors. See `smarter-sphinx-docs`.

## When the user reports that something didn't happen

If the user says that something didn't happen, e.g. "it did not create a
release", "PyPI still has the old version" or "the SDK still rejects that
field", that is a problem to fix, not a claim to debate. Don't answer with
evidence that it did happen somewhere else, e.g. a prerelease on `alpha` or
TestPyPI when they mean `main` and PyPI, or a platform change on `../smarter`'s
`alpha` that their installation doesn't run. Find out what is missing from
their point of view, why, and fix it, or hand them the one command or click
that fixes it.

## Pattern-first workflow

The SDK is consistent, and almost every change has a precedent.

1. Identify what kind of change it is: a new endpoint, a new resource kind, a
   model field, a contract change, a transport behavior, a doc page.
2. Find two or three existing implementations of the same kind, newest first,
   and read them in full: the resource module, its model, its tests and
   fixture, its docs page.
3. Copy their structure, naming, docstrings, logging and error handling.
   Don't introduce a new pattern when one exists. For an endpoint, follow
   [Covering a platform endpoint](#covering-a-platform-endpoint-the-pattern).
4. Make the change, then its tests, docstrings and docs.
5. Run the hooks and the tests, and fix what they find.

When existing code disagrees with these skills, the code that is newest and
consistent with most of the SDK wins. Say so in your summary.

## Reading the platform and its siblings

The SDK follows the platform, so most tasks read `../smarter`, and some
`../smarter-types` or `../cache-results` (the model for CI and releases).

- **Read the local checkouts**, not GitHub: grep them like any local code.
  First check that they are current:
  `../smarter/skills/smarter-project-repositories/scripts/repos-status.sh smarter smarter-types cache-results`
  (read only: each checkout's branch, uncommitted changes, and whether it
  matches its remote). A checkout that is behind can mislead you, e.g. a
  platform on `alpha` that has changes `main` lacks. Say so, and give the user
  the `git -C ../<repository> pull` to run. Don't run it yourself: rule 1
  applies to every repository.
- **Each has its own `CLAUDE.md` and skills.** Read them before changing
  anything there, and follow their rules, not this repository's: e.g. the
  platform's tests run in its Docker containers, not on the host.

## Architecture, and why

Each decision below is recorded in `docs/source/adr/`, with the platform ADR that it
follows or adapts. Read the relevant ADR before you change one of them, and
add an ADR when you make a new decision of that size.

- **Writes go through the manifest api** (`/api/v1/cli/apply/`, `delete/`,
  ...), exactly as the cli sends them. The platform's brokers validate
  manifests and apply business rules there. The REST endpoints' own POST and
  PATCH handlers are inconsistent (raw ORM creates, unvalidated attribute
  setting), so the SDK uses REST only to **read** resources and for **actions**
  that the manifest api has no verb for (evaluate a Guardrail, call an MCP tool,
  search a vectorstore).
- **Models allow extra fields.** The platform adds fields in minor releases,
  and an SDK that rejected them would break on every upgrade. For the same
  reason, values that the platform may add to (a plugin's class, a progress
  event's type) are `str`, not `Literal`.
- **The platform's Pydantic models can't be imported**: both packages are
  named `smarter`, and the platform's models depend on Django. So:
  - the **SAM models** are generated from the JSON Schema of each kind that
    the platform commits in `smarter/smarter/apps/api/v1/contract/sam/`
    (`scripts/generate_sam_models.py`, `make sam-models`), and tested against
    the platform's committed example manifests,
  - the **chat and journal contracts** are hand-mirrored in
    `smarter/models/chat.py` and `journal.py`, and `tests/test_contracts.py`
    checks them against the platform's committed schemas and examples
    (`scripts/sync-contracts.sh`, `make contracts`),
  - the **cli api** is published as `openapi.json`, beside the SAM schemas,
    and `tests/test_contracts.py` checks that every cli request of the SDK is
    one of its operations, and that the SDK calls every operation,
  - the **React contract** (`smarter/models/react.py`) is pure Pydantic, and
    is copied from `smarter.lib.django.templatetags.smarter_react_contract`.
- **Configuration follows ADR-007**: one Pydantic settings model,
  `SmarterSettings`, reads the environment. The lookup order is arguments,
  `SMARTER_*` variables, the cli's `~/.smarter/config.yaml`, then defaults.
- **Logging follows ADR-011's intent** with the standard library: the
  `smarter.*` logger hierarchy, no handlers unless `SMARTER_LOG` is set, and api
  keys masked with `mask_secret()`.
- **The chat contract is always version 2**: every request sends
  `X-Smarter-Capabilities: chat-contract-v2`.

## Covering a platform endpoint (the pattern)

1. Find the view and its url in `../smarter/smarter/smarter/apps/<app>/api/v1/`.
   Read what it reads from the request and what it returns.
2. Probe it on the local platform with a throwaway api key
   (`smarter-api-testing`) and save the real response in your scratchpad.
3. Add or extend the model in `smarter/models/<family>.py`: the fields that
   callers need, typed, `Optional` unless always present, on
   `SmarterCamelModel` when the response is camelCase.
4. Add the method to `smarter/resources/<family>.py`, copying its neighbors:
   `self._http.request(method, path, cast_to=Model, ...)`, ids through
   `resource_id()`, a reST docstring with an example in the module docstring.
5. Add a sanitized fixture to `tests/data/`, a unit test in
   `tests/test_<family>.py`, and a call in `tests/live/test_live.py` if it is
   safe (no deploy, no destructive change to existing data).
6. Run `make test`, `make test-live`, and the hooks.
7. Update the user guide in `docs/source/`, add the module to the api
   reference if it is new, and run `make sphinx-build` (`smarter-sphinx-docs`).

A **new resource kind** on the platform usually needs: `make sam-models`, a
resource class (subclass `SmarterKindResource`, set `kind`, `path`, `model`),
an attribute on `Smarter`, and its tests and docs.

## Platform bugs

The SDK sees the platform from outside, so it finds the platform's bugs. When
an endpoint misbehaves, don't paper over it silently: work around it in the SDK
only when the workaround is harmless (e.g. `Manifests.get()` filters by name
client-side), say so in a comment, make the live test skip with the platform's
message rather than fail, and report the bug to the user.

## Logging

The SDK is a library: it logs to the `smarter.*` logger hierarchy and adds no
handlers unless `SMARTER_LOG` is set (`smarter/core/log.py`). Copy the calls in
`smarter/core/http.py` and `conf.py`:

```python
logger = logging.getLogger(__name__)
logger.warning("smarter cli configuration %s is invalid and was ignored: %s", path, e)
```

- %-style arguments, never f-strings: a message that isn't emitted is never
  formatted, and aggregators can group messages by their template. Wrap an
  expensive argument in `if logger.isEnabledFor(logging.DEBUG):`.
- The logger's name says where a message came from, so the SDK's messages
  don't carry the platform's `ClassName.method()` prefix. Say what happened
  and why, in words a caller can act on.
- Pick the level deliberately: `debug` for request and response bodies,
  `info` for one line per request and each retry, `warning` for something
  unusual that was handled (an ignored configuration file). An error the
  caller receives as an exception isn't logged as well.
- **Never log a secret.** Mask an api key with `mask_secret()`; never log a
  whole headers dict or `SmarterSettings`. A request body can hold a secret,
  e.g. a `Secret` manifest's value, so only `debug` logs bodies.

## Which skill to load

| Task                                                              | Skill                    |
| ----------------------------------------------------------------- | ------------------------ |
| Unit tests, live tests, fixtures, coverage                        | `smarter-python-testing` |
| Probing the platform's api by hand                                | `smarter-api-testing`    |
| Python docstrings                                                 | `smarter-docstrings`     |
| Type annotations, `Any`, the `smarter.core.typing` aliases        | `smarter-python-typing`  |
| The SDK's Sphinx docs site, its ADRs and its Terraform            | `smarter-sphinx-docs`    |
| CI, Codecov, requirements, semantic-release, publishing a release | `smarter-python-release` |
| Lint, format, pre-commit                                          | `smarter-code-quality`   |
| Writing a commit message                                          | `smarter-git-commits`    |
| Monthly sync with the platform, and requirements updates          | `monthly-maintenance`    |
| A platform contract change to follow now, between maintenances    | `smarter-contract-sync`  |

The platform's own skills (`../smarter/skills/`) apply whenever you change the
platform itself, e.g. to fix a bug that the SDK found.

## Definition of done

- The change follows an existing pattern in this repository, and its ADRs.
- Unit tests cover it, you ran `make test` yourself and it passes, and
  coverage stays at 95% or more. Report failures honestly, including
  pre-existing ones.
- The live tests pass against the local platform, or their skips name platform bugs.
- The pre-commit hooks pass on the changed files.
- Public objects have reST docstrings, the docs in `docs/source/` describe the
  feature, and `make sphinx-build` passes.
- Your summary says what changed, what you verified, what you skipped, and any
  platform bugs you found.
