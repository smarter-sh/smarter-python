---
name: smarter-code-quality
description: Use before finishing any change to the smarter-python SDK, to lint and format it with the repository's pre-commit hooks (black, flake8, isort, autoflake, bandit, codespell, pyupgrade, pydocstringformatter, Prettier, commitlint). Explains which tools are authoritative, how to run them on changed files under zsh, and the traps (untracked files, capitalized docstrings, generated SAM models, PYTHONPATH, a prettier cache folder).
---

# Smarter Python SDK Code Quality

`.pre-commit-config.yaml` at the repository root is the authoritative standard.
It is cache-results' (`../cache-results/.pre-commit-config.yaml`), the model for
every Smarter PyPI package, with two differences: prettier skips `tests/data/`,
and autoflake has `--in-place`. Keep them otherwise the same. If a hook passes,
the code meets the standard. If it fails, fix the code. Never bypass a hook
(`--no-verify`, `SKIP=`, blanket `# noqa`). CI's `lint` job runs every hook on
every file, so a bypassed hook fails the pull request anyway.

## What the hooks enforce

| Hook                 | Configuration                            | Notes                                                                                                            |
| -------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| black                | `pyproject.toml`, line length 120        | Formatter. Let it reformat.                                                                                      |
| isort                | `pyproject.toml`, `profile = black`      | Import order. Don't add `lines_after_imports`: it fights black forever.                                          |
| autoflake            | `--in-place --remove-all-unused-imports` | Deletes unused imports. Needs `--in-place`, which setting `args` drops from the hook's defaults.                 |
| flake8               | `.flake8`, line length 120               | pyflakes and pycodestyle. Skips the generated `smarter/models/sam/*`.                                            |
| bandit               | `-ll`                                    | Medium or high severity security findings fail.                                                                  |
| pyupgrade            | `--py310-plus`                           | Modern syntax, e.g. `X \| None` rather than `Optional[X]` (Python 3.10+).                                        |
| pydocstringformatter |                                          | Normalizes docstring layout. See `smarter-docstrings`.                                                           |
| codespell            |                                          | No ignore list. Reword, or fix the spelling.                                                                     |
| prettier             | `.prettierignore`                        | Markdown, YAML and JSON. Skips `tests/data/` (copied from the platform) and `CHANGELOG.md` (semantic-release's). |

Also: trailing whitespace, end-of-file newline, YAML/JSON/TOML syntax, merge
conflict markers, private keys, debug statements, and commitlint
(`commitlint.config.js`) on commit messages, at the `commit-msg` stage.
semantic-release reads the same messages: see `smarter-git-commits`.

**ruff is not configured.** Don't report ruff output as lint debt.

## How to run

From the repository root, with `PYTHONPATH` the root (never `./smarter`):

```console
make init                    # once: the venv, the package, and the pre-commit and commit-msg hooks
export PYTHONPATH=.
git diff --name-only | xargs venv/bin/pre-commit run --files
git ls-files --others --exclude-standard | xargs venv/bin/pre-commit run --files   # new files
make pre-commit-run          # every hook on every tracked file (= make lint)
make pre-commit-init         # reinstall the hooks and update their versions (pre-commit autoupdate)
```

- **`--all-files` skips untracked files**: it uses `git ls-files`. Check a new
  file with `--files`.

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
- `make pre-commit-run` is slower, and touches files you didn't change. Use
  it before a pull request, and `--files` while you work.
- **The prettier hook can leave a `node_modules/.cache/` folder** in the
  repository root. It is git-ignored; `make clean` removes it. Don't pass it to
  the hooks.
- `make pre-commit-init`, and so `make init`, runs `pre-commit autoupdate`,
  which edits `.pre-commit-config.yaml`. That change is a commit of its own
  (`build:`): don't fold it into an unrelated one.

## Principles

- Match the surrounding code: its naming, comment density, logging
  (`logger = logging.getLogger(__name__)`, never the api key), and the
  exceptions of `smarter.core.exceptions`.
- Fix the cause of a finding. Suppress one only with a narrow, commented
  directive that explains why (e.g. `# nosec B311 - jitter, not security`).
- Don't reformat code you didn't otherwise change. It buries the real diff.
