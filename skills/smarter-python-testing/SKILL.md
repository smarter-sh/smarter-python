---
name: smarter-python-testing
description: Use when writing, fixing or running the smarter-python SDK's tests, or raising its coverage. Covers the unit tests (SmarterTestBase, routes answered by an httpx MockTransport, sanitized fixtures in tests/data), the opt-in live tests against a running Smarter platform, the contract and SAM model tests, coverage, and what never to do in a test.
---

# Smarter Python SDK Testing

## Two kinds of tests

| Kind | Where                     | Reaches a platform? | Runs in CI | Command                                     |
| ---- | ------------------------- | ------------------- | ---------- | ------------------------------------------- |
| Unit | `tests/test_<module>.py`  | Never               | Yes        | `make test`                                 |
| Live | `tests/live/test_live.py` | Yes                 | No         | `make test-live` (`SMARTER_TEST_LIVE=true`) |

Run them on the host, with the virtual environment, from the repository root.
The SDK has no containers of its own:

```console
PYTHONPATH=. venv/bin/python -m unittest discover -s tests -t .
PYTHONPATH=. venv/bin/python -m unittest tests.test_llmclients
make coverage
```

`PYTHONPATH` must be `.` (the repository root). A developer shell that exports
`PYTHONPATH=./smarter` breaks every import: see `smarter-python-development`.

Run the tests yourself, after every change, and report the counts.

## Unit tests

- One module per source module: `smarter/resources/guardrails.py` is tested by
  `tests/test_guardrails.py`.
- Subclass `SmarterTestBase` (`tests/base.py`), the SDK's counterpart of the
  platform's base class (ADR-013). Each test gets `self.client`, a `Smarter`
  whose requests are answered by an `httpx.MockTransport`. It also hides the
  developer's `SMARTER_*` variables and `~/.smarter/config.yaml`, so that a
  local configuration can't change a result.
- Register answers with `self.route(method, path, fixture=..., json_body=...,
status=..., text=..., handler=...)`. `path` is relative to `/api/v1/`. An
  unrouted request gets a 404.
- Assert what was sent with `self.last_request`, `self.request_json()` and
  `self.last_request.url.params`.
- `self.make_client(max_retries=2, ...)` builds another client on the same
  routes. Patch `smarter.core.http.time.sleep` when a test retries.

## Fixtures

- Fixtures are **real platform responses**, trimmed and sanitized, in
  `tests/data/<name>.json` (and `prompt_sse.txt` for a stream). Don't invent a
  response shape: probe the endpoint first (`smarter-api-testing`).
- **Sanitize before saving.** Replace names, emails, addresses, phone numbers,
  account numbers, api keys (even masked ones), tool call ids and private
  hostnames with placeholders (`Example Company`, `user@example.com`,
  `1234-5678-9012`). Then grep `tests/data/` for what you replaced. The
  repository is public.
- `tests/data/contracts/` and `tests/data/sam/` are copies of what the platform
  publishes. Refresh them with `make contracts` and `make sam-models`, never by
  hand.

## Contract and model tests

- `tests/test_contracts.py` fails when the platform's chat or journal contract
  has a field that the SDK's mirror doesn't declare, or when the platform's
  example of a version 2 model doesn't parse. Fix the mirror in
  `smarter/models/chat.py` or `journal.py`.
- `tests/test_sam.py` fails when a generated SAM model doesn't parse its
  kind's example manifest, or a kind's model is missing. Regenerate, don't
  edit the generated code.

## Live tests

```console
SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=<throwaway key> make test-live
```

- They validate every model against the platform's real responses, including
  `describe` of a real resource of every kind parsed as its SAM model.
- They prompt an LLMClient (`SMARTER_TEST_LLMCLIENT`, default `calculator`),
  which makes **billable LLM requests**. That is accepted in this project.
- They apply and delete a throwaway Guardrail named `sdk_live_test_<hash>`,
  with `addCleanup`. Anything a live test creates, it deletes.
- **They never deploy, undeploy, snapshot, restore, or delete existing
  data.** Deploy creates real, billable infrastructure.
- A platform error (an `APIStatusError`) skips the subtest with the platform's
  message. An SDK error (e.g. `APIResponseValidationError`) fails it. Read the
  skip reasons: they are platform bugs to report.

Create and delete the throwaway api key as `smarter-api-testing` describes.

## Coverage

At least 95%, with branch coverage: `[tool.coverage]` in `pyproject.toml` sets
`fail_under = 95`, so `make coverage` and every CI test job fail below it, and
Codecov checks 95% of the project and of each pull request's patch
(`codecov.yml`). `if TYPE_CHECKING:` blocks are excluded. Test
behavior through the public interface (the client's methods), not private
helpers.

## Reporting

Report pass, fail, error and skip counts honestly, for both suites. Name the
live tests' skips, and separate platform bugs from SDK failures.
