---
name: monthly-maintenance
description: Use when asked to do smarter-python's monthly maintenance, or either half of it - (1) bring the SDK back in sync with the Smarter platform by reviewing the platform's commits since smarter-python's last release and changing the SDK, its models, tests and docs as needed, and (2) update all of the SDK's Python requirements files, retest, and, if the tests pass, write a "fix" git commit. Covers finding the baseline, reading the delta by area, the mechanical refreshes (SAM models, contracts, api reference), the dependency update and its tests, and the commit messages.
---

# smarter-python Monthly Maintenance

The SDK covers a platform that changes every week. Once a month, this
maintenance brings it back in step, and keeps its dependencies current. It has
two parts, done in this order, each with its own commit:

1. **Sync with the platform** (Part 1).
2. **Update the requirements and retest** (Part 2), so that the retest covers
   the sync too.

Load `smarter-python-development` first. Its rules apply throughout, in
particular: **never run git write commands** (write the commit command as text,
see `smarter-git-commits`), **never deploy from a test or probe**, and run the
tests yourself.

Work from the smarter-python repository root, with the platform checked out at
`../smarter` and its local dev server running (`../smarter`: `make run`; the
platform's `smarter-docker-environment` skill).

## Part 1: Sync with the platform

### 1. Find the delta

```console
skills/monthly-maintenance/scripts/smarter-delta.sh
```

It fetches the platform (`git fetch` only updates its remote-tracking
branches), and lists the platform's commits on `origin/main`, its released
branch, since a baseline, grouped by what they mean for the SDK, with a diff
stat per area. The baseline is the later of:

- the platform's commit at the date of smarter-python's **last release tag**,
  and
- the commit named by the newest `Synced with smarter <sha>` line in
  smarter-python's commit history, which every maintenance sync records (see
  step 5).

Pass an explicit base as the third argument to override it, e.g. when the SDK
was synced with an unreleased platform branch:
`smarter-delta.sh ../smarter origin/main <sha>`.

If the platform's release that users run is not `origin/main`, ask the user
which ref to sync with.

### 2. Review each area

For each area with changes, read the diffs, not only the subjects:

```console
git -C ../smarter diff <base>..origin/main -- <path>
git -C ../smarter show <sha>
```

| Area in the report                      | What to check, and what to change in the SDK                                                                                                                         |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Manifest (cli) api                      | New or changed verbs, parameters, responses: `smarter/resources/manifests.py`, `smarter/client.py` (`whoami`, `version`, `kinds`)                                    |
| REST urls and views                     | New endpoints to cover, changed paths, parameters, bodies or permissions: `smarter/resources/<family>.py`                                                            |
| Serializers                             | Changed REST response fields: `smarter/models/<family>.py`, and the fixtures in `tests/data/`                                                                        |
| SAM manifest models and kinds           | A new, renamed or removed kind, or a changed spec: `make sam-models SMARTER_REF=origin/main`, then a resource class for a new kind with a REST api                   |
| Chat and journal contracts, cli OpenAPI | `make contracts SMARTER_REF=origin/main`, then fix `smarter/models/chat.py`, `journal.py` or `smarter/resources/manifests.py` until `tests/test_contracts.py` passes |
| Django-React contract                   | Copy the change into `smarter/models/react.py`                                                                                                                       |
| Authentication                          | Headers, schemes, token formats: `smarter/core/http.py`                                                                                                              |
| Platform settings that gate apis        | e.g. a new `SMARTER_ENABLE_*` switch: the docs, and the live tests' skips                                                                                            |
| ADRs                                    | A new or changed platform ADR that the SDK follows or adapts: `doc/adr/`                                                                                             |
| Skills                                  | A change to a platform skill that a skill here adapts: the adapted copy in `skills/`                                                                                 |
| Lint standard                           | Hook or tool configuration changes: `.pre-commit-config.yaml`, `pyproject.toml`, `.flake8`                                                                           |
| The SDK's own docs pages                | Someone edited them in the platform: keep the edit, and make sure the generated reference still matches                                                              |

Follow the pattern in `smarter-python-development` ("Covering a platform
endpoint") for every change: probe the real endpoint (`smarter-api-testing`),
model it, add a sanitized fixture and a unit test, and a live test when it is
safe.

Notes:

- **Everything comes from the platform's committed contract**, in
  `../smarter/smarter/smarter/apps/api/v1/contract/` (the SAM schemas and
  examples, and `openapi.json`), plus the chat and journal contracts. Pass the
  ref you sync with, e.g. `SMARTER_REF=origin/main`, so that the files are read
  with `git show` at that ref, not from `../smarter`'s working tree. No running
  platform is needed.
- **`tests/test_contracts.py` fails when the platform adds a cli operation**
  that the SDK doesn't call (`TestOpenApiContract`). Cover it, or add it to
  `NOT_CALLED` with a reason.
- **Removals and renames are breaking changes** for the SDK's users. Keep the
  old name as a deprecated alias for a release when that is cheap, and say so
  in the commit body.
- **Not every platform change concerns the SDK.** Internal refactors, Django
  views of the web console, React apps, migrations, Celery tasks and
  infrastructure are out of scope unless they change the api.

### 3. Refresh what is generated

```console
make sam-models SMARTER_REF=origin/main    # copies every contract, then regenerates smarter/models/sam/
PYTHONPATH=. venv/bin/python scripts/generate_reference.py
skills/smarter-sphinx-docs/scripts/check-sdk-pages.sh
```

Regenerate the api reference whenever a docstring changed, and update the
SDK's guide pages in `../smarter/docs/source/smarter-framework/smarter-python/`
for any user-visible change (`smarter-sphinx-docs`).

### 4. Test

```console
make test
SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=<throwaway key> make test-live
git diff --name-only | xargs venv/bin/pre-commit run --files
git ls-files --others --exclude-standard | xargs venv/bin/pre-commit run --files
```

Read the live tests' skip reasons. A new skip is either a platform bug to report
or an SDK gap to fix.

### 5. Commit

Write the commit command (never run it), following `smarter-git-commits`. Its
type follows the change: `feat` when the SDK covers something new, `fix` when it
corrects drift. The body lists the platform commits that each change follows,
and ends with this line, which the next run's baseline reads:

```text
Synced with smarter <full sha of the platform ref you synced with>
```

Get the sha with `git -C ../smarter rev-parse origin/main`. Changes in
`../smarter` (the SDK's docs) get their own commit command, for that repository.

If nothing in the delta concerns the SDK, there is no commit. Report that, with
the range you reviewed.

## Part 2: Update the requirements and retest

### The files

| File                     | What it holds                                      | How it is updated                                                                   |
| ------------------------ | -------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `requirements/base.txt`  | The runtime dependencies, as **compatible ranges** | Widen an upper bound for a new major version, once the tests pass with it (ADR-011) |
| `requirements/local.txt` | The development tools, **pinned**                  | Pin each to its latest version                                                      |
| `requirements/*.in`      | Includes of the `.txt` files                       | Unchanged, unless a file is added                                                   |

The SDK is a library, so its runtime dependencies are never pinned: an
application must be free to pin its own versions.

### 1. See what is outdated

```console
PYTHONPATH= venv/bin/pip install --upgrade pip
PYTHONPATH= venv/bin/pip install -r requirements/local.txt
PYTHONPATH= venv/bin/pip list --outdated
```

### 2. Update

- **local.txt:** set every pin to its latest version. Keep `black`, `isort`,
  `flake8`, `bandit`, `codespell`, `pyupgrade` and `pydocstringformatter` at the
  versions that `.pre-commit-config.yaml` uses, or newer, so that the venv's
  tools and the hooks agree. The hooks' own versions are bumped weekly by the
  `precommitVersionBumps` workflow, so don't edit `.pre-commit-config.yaml` here
  unless the hooks are behind.
- **base.txt:** for each runtime dependency whose newest version is outside its
  range (a new major version), raise the upper bound. Raise a lower bound only
  when the SDK starts to need a newer feature, and say which.
- Install the result: `PYTHONPATH= venv/bin/pip install --upgrade -r requirements/local.txt`.

### 3. Retest

```console
make test                                                   # the newest versions
skills/monthly-maintenance/scripts/test-minimum-versions.sh # the lowest versions that base.txt allows, on Python 3.10
SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=<throwaway key> make test-live
git ls-files '*.py' | xargs venv/bin/pre-commit run --files  # new tool versions may reformat
PYTHONPATH= venv/bin/python -m build --outdir "$SCRATCHPAD/dist" .  # the sdist and wheel
venv/bin/twine check "$SCRATCHPAD"/dist/*
```

Don't use `make build` here: it runs `make init`, which deletes and recreates the
virtual environment. Build into your scratchpad, not `dist/`.

`test-minimum-versions.sh` matters as much as `make test`: the development
venv has the newest versions, and leftovers of older requirements, so it can't
show that `base.txt`'s ranges hold. It once found a missing runtime dependency
(`email-validator`, which the SAM models' `EmailStr` needs) that every other
test missed. The build check matters too: it once found that the sdist lacked
`requirements/base.txt`, which `setup.py` reads, so no wheel could be built.

If a test fails:

- fix the SDK when the fix is small and clearly right (e.g. a deprecation),
- otherwise keep the previous version of that package (the previous pin, or the
  previous upper bound), retest, and report the failure, with its output.

### 4. Commit

Only when every test passes, write the commit command (never run it), following
`smarter-git-commits`:

```console
git commit --author="Claude <noreply@anthropic.com>" \
  -m "fix(deps): update the python requirements" \
  -m "Monthly maintenance: every development tool in requirements/local.txt is pinned to its latest version, and requirements/base.txt's ranges admit the latest runtime versions." \
  -m "requirements/local.txt:" \
  -m "- black 26.10.0 -> 26.11.0
- ..." \
  -m "requirements/base.txt:" \
  -m "- no change: every runtime dependency's newest version is within its range" \
  -m "Tests: make test (125 passed, 9 skipped), test-minimum-versions.sh on Python 3.10 (125 passed, 9 skipped), make test-live (9 passed, n subtests skipped for platform bugs), pre-commit, and the sdist and wheel built and checked by twine." \
  -m "Co-authored-by: Lawrence McDaniel <lpm0073@gmail.com>"
```

`fix` makes semantic-release publish a patch release, which ships the
dependency updates. List every version change, and the real test counts. If
nothing was outdated, there is no commit: report that.

## Report

End with a summary for the user:

- the platform range that was reviewed, and what changed in the SDK because of it,
- the platform changes that were deliberately not followed, and why,
- platform bugs found (new live test skips),
- the dependency updates, and any that were held back, with the failing output,
- the test results of every suite,
- the commit commands, one per repository and part.
