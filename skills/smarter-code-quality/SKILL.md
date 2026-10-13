---
name: smarter-code-quality
description: Use before finishing any change to the smarter-python SDK, to lint and format it with the repository's pre-commit hooks (black, flake8, isort, autoflake, bandit, codespell, pyupgrade, pydocstringformatter, Prettier). Explains which tools are authoritative, how to run them on changed files under zsh, and the traps (generated SAM models, PYTHONPATH).
---

# Smarter Python SDK Code Quality

`.pre-commit-config.yaml` at the repository root is the authoritative standard,
and it matches the platform's (`../smarter/.pre-commit-config.yaml`), minus the
React hooks. If a hook passes, the code meets the standard. If it fails, fix the
code. Never bypass a hook (`--no-verify`, `SKIP=`, blanket `# noqa`).

## What the hooks enforce

| Hook                 | Configuration                       | Notes                                                                          |
| -------------------- | ----------------------------------- | ------------------------------------------------------------------------------ |
| black                | `pyproject.toml`, line length 120   | Formatter. Let it reformat.                                                    |
| isort                | `pyproject.toml`, `profile = black` | Import order. Don't add `lines_after_imports`: it fights black forever.        |
| autoflake            | `--remove-all-unused-imports`       | Deletes unused imports. Re-check that nothing you need was removed.            |
| flake8               | `.flake8`                           | Selects **only C101** (coding magic comment). It is not a general style check. |
| bandit               | `-ll`                               | Medium or high severity security findings fail.                                |
| pyupgrade            |                                     | Modern syntax. The SDK supports Python 3.10 and later.                         |
| pydocstringformatter |                                     | Normalizes docstring layout. See `smarter-docstrings`.                         |
| codespell            | `codespell.txt` ignore list         | Skips `tests/data/`. Add real project words to `codespell.txt`.                |
| prettier             |                                     | Markdown, YAML and JSON. Skips `tests/data/`.                                  |

Also: trailing whitespace, end-of-file newline, YAML/JSON/TOML syntax, merge
conflict markers, private keys, AWS credentials, debug statements, and
commitlint on commit messages.

**ruff is not configured.** Don't report ruff output as lint debt.

## How to run

From the repository root, with `PYTHONPATH` the root (never `./smarter`):

```console
export PYTHONPATH=.
git diff --name-only | xargs venv/bin/pre-commit run --files
git ls-files --others --exclude-standard | xargs venv/bin/pre-commit run --files   # new files
```

- Use `xargs`. Under zsh, `pre-commit run --files $FILES` passes one argument,
  and pre-commit checks nothing.
- Hooks that modify files fail the first run, then pass. Run them until they
  pass, and read the diff of what they changed.
- **pydocstringformatter capitalizes a docstring's first word**, so
  `"""sam_model() looks..."""` becomes `"""Sam_model() looks..."""`. Start such a
  docstring with the name in double backticks (` """`sam_model()`looks..."""`),
  or rephrase it.
- `smarter/models/sam/` is generated. The hooks reformat it like any other
  code, which is fine. Don't hand-edit it to satisfy a hook: change
  `scripts/generate_sam_models.py` instead.
- `make pre-commit-run` runs every hook on every file.

## Principles

- Match the surrounding code: its naming, comment density, logging
  (`logger = logging.getLogger(__name__)`, never the api key), and the
  exceptions of `smarter.core.exceptions`.
- Fix the cause of a finding. Suppress one only with a narrow, commented
  directive that explains why (e.g. `# nosec B311 - jitter, not security`).
- Don't reformat code you didn't otherwise change.
