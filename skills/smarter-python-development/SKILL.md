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
| `scripts/`                                         | `generate_sam_models.py`, `sync-contracts.sh`, `generate_reference.py`               |
| `tests/`                                           | Unit tests (`tests/test_*.py`), fixtures (`tests/data/`), live tests (`tests/live/`) |
| `doc/adr/`                                         | The SDK's architecture decision records, which adapt the platform's                  |
| `skills/`                                          | These skills                                                                         |

The SDK's documentation lives in the **platform's** repository:
`../smarter/docs/source/smarter-framework/smarter-python*`. See
`smarter-sphinx-docs`.

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
6. **Coverage:** at least 90% overall, 95% where it takes moderate effort.
   CI fails below 90%.
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

## Architecture, and why

Each decision below is recorded in `doc/adr/`, with the platform ADR that it
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
7. Update the docs page in `../smarter/docs/source/smarter-framework/smarter-python/`
   and regenerate the api reference (`smarter-sphinx-docs`).

A **new resource kind** on the platform usually needs: `make sam-models`, a
resource class (subclass `SmarterKindResource`, set `kind`, `path`, `model`),
an attribute on `Smarter`, and its tests and docs.

## Platform bugs

The SDK sees the platform from outside, so it finds the platform's bugs. When
an endpoint misbehaves, don't paper over it silently: work around it in the SDK
only when the workaround is harmless (e.g. `Manifests.get()` filters by name
client-side), say so in a comment, make the live test skip with the platform's
message rather than fail, and report the bug to the user.

## Which skill to load

| Task                                                       | Skill                    |
| ---------------------------------------------------------- | ------------------------ |
| Unit tests, live tests, fixtures, coverage                 | `smarter-python-testing` |
| Probing the platform's api by hand                         | `smarter-api-testing`    |
| Python docstrings                                          | `smarter-docstrings`     |
| Type annotations, `Any`, the `smarter.core.typing` aliases | `smarter-python-typing`  |
| The SDK's pages in the platform's Sphinx docs              | `smarter-sphinx-docs`    |
| Lint, format, pre-commit                                   | `smarter-code-quality`   |
| Writing a commit message                                   | `smarter-git-commits`    |
| Monthly sync with the platform, and requirements updates   | `monthly-maintenance`    |

The platform's own skills (`../smarter/skills/`) apply whenever you change the
platform itself, e.g. to fix a bug that the SDK found.

## Definition of done

- The change follows an existing pattern in this repository, and its ADRs.
- Unit tests cover it, `make test` passes, and coverage stays at 90% or more.
- The live tests pass against the local platform, or their skips name platform bugs.
- The pre-commit hooks pass on the changed files.
- Public objects have reST docstrings, and the docs in `../smarter/docs/source/`
  describe the feature.
- Your summary says what changed, what you verified, what you skipped, and any
  platform bugs you found.
