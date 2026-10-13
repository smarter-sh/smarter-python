---
name: smarter-sphinx-docs
description: Use when adding or editing the smarter-python SDK's documentation, which lives in the Smarter platform's Sphinx docs (../smarter/docs/source/smarter-framework/smarter-python*, published to docs.smarter.sh), or when regenerating the SDK's api reference pages. Covers where each page goes, the generated reference and why it is generated, the evergreen-prose rule, and how to verify without the platform's 20-minute build.
---

# The SDK's Sphinx Documentation

The SDK has no docs folder of its own. Its documentation is a section of the
platform's docs, in the platform's repository, so that docs.smarter.sh is one
site:

| Content                                        | Location (in `../smarter/docs/source/`)                                      |
| ---------------------------------------------- | ---------------------------------------------------------------------------- |
| The SDK's landing page: what it is, SDK vs CLI | `smarter-framework/smarter-python.rst`, in `smarter-framework.rst`'s toctree |
| Guides: configuration, manifests, chat, ...    | `smarter-framework/smarter-python/<topic>.rst`                               |
| The api reference, **generated**               | `smarter-framework/smarter-python/reference/**`                              |
| The SDK's own architecture decisions           | Not here: `doc/adr/` in this repository                                      |

Load the platform's own `smarter-sphinx-docs` skill (`../smarter/skills/`) for
its general rules: headings (`=`, `-`, `~`, `^`), toctrees, code blocks, and
writing for a reader new to Smarter.

## The api reference is generated

The platform's Sphinx build autodocs the platform's own `smarter` package, and
the SDK's import name is `smarter` too, so that build can't import the SDK.
`scripts/generate_reference.py` imports the SDK here, and writes its docstrings
as `py:` domain directives (`.. py:class::`, `.. py:method::`, ...), which need no
import:

```console
PYTHONPATH=. venv/bin/python scripts/generate_reference.py      # writes into ../smarter
```

- **Never edit the generated pages.** Fix the docstring (`smarter-docstrings`)
  and regenerate.
- A new module must be added to `PAGES` in `scripts/generate_reference.py`.
- The SDK's module paths must not collide with the platform's, or the two
  packages' objects collide in the shared Sphinx index. That is why the SDK's
  internals are `smarter.core`, not `smarter.common` (which the platform has).
  Check `ls ../smarter/smarter/smarter` before you add a top-level SDK module.

## Writing rules

- **Evergreen prose**, as in the platform: no "New in 0.2" sections. Weave a
  feature into the page where its topic belongs.
- Every example must run. Check the field paths of SAM models against the
  generated code (e.g. an LLMClient's provider is
  `spec.config.prompt.provider`), and run the example against fixtures or the
  local platform.
- Link the platform's resource pages with `:doc:`, e.g.
  `:doc:`Guardrails <../../smarter-resources/smarter-guardrail>``.
- Say when an operation is **billable** (prompts) or creates **real
  infrastructure** (deploy).

## Verify (never the full build)

1. Links, with the platform's checker, from `../smarter`:

   ```console
   cd ../smarter && skills/smarter-sphinx-docs/scripts/check-docs.sh \
     docs/source/smarter-framework/smarter-python.rst docs/source/smarter-framework/smarter-python/*.rst \
     docs/source/smarter-framework/smarter-python/reference/*.rst docs/source/smarter-framework/smarter-python/reference/sam/*.rst
   ```

2. The reST itself, with a build of **only the SDK's pages**, which takes
   seconds: [scripts/check-sdk-pages.sh](scripts/check-sdk-pages.sh). It reports
   every warning except links to pages outside the SDK's section. It must report
   none.

The user builds the full docs.
