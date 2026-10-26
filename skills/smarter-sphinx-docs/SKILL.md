---
name: smarter-sphinx-docs
description: Use when adding or editing the smarter-python SDK's Sphinx documentation in docs/source, published to https://docs.smarter-python.smarter.sh/ - the getting-started pages, the user guide, the api reference generated from docstrings by autodoc, the architectural decision records (ADRs) in docs/source/adr - or when building, publishing, or changing the site's AWS hosting (terraform/docs). Covers the layout, headings and toctrees, autodoc pages, the generated SAM models' pages, how to write an ADR, links to the platform's docs, the evergreen-prose rule, make sphinx-build (warnings are errors), make sphinx-publish, and the Terraform stack.
---

# The SDK's Sphinx Documentation

The docs live in `docs/source/`, built by Sphinx with the Read the Docs theme
and published to **https://docs.smarter-python.smarter.sh/**. Extensions
(`docs/source/conf.py`): autodoc, intersphinx (Python's and Pydantic's docs),
viewcode, copybutton, `notfound.extension` (the 404 page) and `sphinx_sitemap`.
They follow the platform's conventions (`../smarter/skills/smarter-sphinx-docs`),
on a much smaller site. The platform's docs (docs.smarter.sh) keep one short
page about the SDK, `smarter-framework/smarter-python.rst`, that links here.

## Build to verify

Unlike the platform's 20-minute build, this one takes seconds. Build after
every docs or docstring change:

```console
make sphinx-build      # rm -rf docs/build, then sphinx-build -W --keep-going: every warning is an error
open docs/build/html/index.html
make sphinx-linkcheck  # every external link, when you've added some
```

It must succeed with no warnings. autodoc imports the SDK from the repository
root (never `./smarter`, see `smarter-python-development`). intersphinx fetches
Python's and Pydantic's inventories, so the build needs the network. CI builds
it on every push and pull request.

`-W` catches malformed reST (a heading underline shorter than its title, a
directive whose content doesn't follow a blank line, a page in no toctree),
but not a page that renders wrong. Open each page you changed and read it:
code-block content indented consistently, lists that render as lists, links
that land where they should.

## Layout

| Content                          | Location                                                                   |
| -------------------------------- | -------------------------------------------------------------------------- |
| Landing page, badges, toctrees   | `index.rst`: Getting Started, User Guide, Reference, Project               |
| Getting started                  | `installation.rst`, `quickstart.rst`                                       |
| User guide, one topic per page   | `guide/*.rst`: configuration, manifests, chat, resources, models, errors   |
| API reference                    | `reference.rst`, and one autodoc page per module family in `reference/`    |
| The SAM models                   | `reference/sam.rst`, and one page per kind in `reference/sam/<module>.rst` |
| Changelog, contributing, license | `project/*.rst`                                                            |
| Architectural decision records   | `adr.rst` (the toctree), and `adr/NNN-<slug>.rst`                          |
| The footer's attribution         | `_templates/footer.html`: The Smarter Project, on every page and the 404   |
| Files copied as they are         | `_extra/` (`robots.txt`)                                                   |

Headings: `=` for the page title, `-` for sections, then `~` and `^`. Every
page must be in a toctree, or the build warns.

## The api reference comes from docstrings

A reference page is a title and `.. automodule::` directives. `conf.py` sets
`members` and `show-inheritance` by default. A new module gets an
`automodule` in its family's page in `reference/`. **A new SAM kind** (after
`make sam-models`) gets `reference/sam/<module>.rst`, titled with its model's
name (e.g. `SAMLLMClient`), and an entry in `reference/sam.rst`'s toctree.
Fix a wrong reference in the docstring, never the `.rst` (`smarter-docstrings`).

Two things in `conf.py` exist for the generated SAM models, which are never
edited by hand:

- Their **field** docstrings come from the platform's JSON Schemas, and are
  plain text, so an `autodoc-process-docstring` hook escapes them (the `*` of
  `models/*` must not start emphasis). Their class docstrings are reST.
- Each module defines its own copy of the classes several kinds share (e.g.
  `SAMPluginCommonMetadata`), so `suppress_warnings = ["ref.python"]` silences
  Sphinx's "more than one target found" for them.

## Cross-references

- **Another page of this site:** `:doc:`, relative to the referring page
  (`` :doc:`manifests` `` from `guide/resources.rst`), or absolute from
  `docs/source/` with a leading `/` (`` :doc:`/reference/client` ``). A missing
  target warns, so the build checks these.
- **A Python object:** `:class:`, `:meth:`, `:func:` with its full dotted
  path, and `~` to show only the last name. Python's and Pydantic's objects
  resolve through intersphinx. `nitpicky` is off, so a wrong path renders as
  plain text without a warning: check the link in the built page.

## Links to the platform's docs

The platform's pages are another site, so link them with absolute urls, never
`:doc:`, e.g.
`` `Guardrails <https://docs.smarter.sh/smarter-resources/smarter-guardrail.html>`__ ``.
docs.smarter.sh serves pages from its root; old `/en/latest/` urls redirect
there, so new links leave it out. Sphinx doesn't check these;
`make sphinx-linkcheck` does. Link a platform ADR
as `Smarter ADR-NNN`, so that it isn't mistaken for one of the SDK's.

## ADRs

One decision each, in Michael Nygard's format, in the format of the platform's
(`../smarter/docs/source/adr/`). Read `adr/000-intro.rst` first.

- **Sections, in order:** Status, Context, Decision, Alternatives Considered,
  Consequences (**Positive:** and **Negative:** lists), Related ADRs.
- **Numbers are aligned** with the Node.js and Go SDKs (`../smarter-nodejs/doc/adr`,
  `../smarter-golang/doc/adr`): a decision every SDK shares takes the same
  number in each; a new one takes the next number free in all of them.
- **Title:** `ADR-NNN: <Decision>`, in a file named `NNN-<slug>.rst`, added to
  `adr.rst`'s toctree.
- **Related ADRs** link this site's ADRs with `:doc:`, and a platform ADR that
  this one adapts with its GitHub url:

  ```rst
  - :doc:`ADR-015: Semantic Versioning and API Versions <015-versioning>`
  - `Smarter ADR-014: CI CD <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/014-ci-cd.rst>`__
  ```

- **Never rewrite a decision.** Add an ADR that supersedes it, and set the old
  one's Status to `Superseded by ADR-NNN` (e.g. ADR-010 by ADR-024).

## Writing rules

- **Evergreen prose**, as in the platform: no "New in 0.2" sections. Weave a
  feature into the page where its topic belongs. The changelog carries the
  history.
- Write for a Python developer new to Smarter. Define a term on first use
  (SAM, manifest, kind, LLMClient), and link the page that explains it, here
  or on docs.smarter.sh.
- **Every example must run.** Check the field paths of SAM models against the
  generated code (e.g. an LLMClient's provider is
  `spec.config.prompt.provider`), and run the example against fixtures or the
  local platform.
- Say when an operation is **billable** (prompts) or creates **real
  infrastructure** (deploy).
- `double backticks` for literals, settings and commands, and
  `.. code-block:: python` or `console` for examples. Console examples start
  with `$ ` (copybutton strips it).
- The README, `index.rst`, `quickstart.rst` and the guide overlap. When
  behavior changes, update all of them in the same change.

## Publishing

```console
make sphinx-publish   # sphinx-build, aws s3 sync --delete, CloudFront invalidation of /*
```

The Release workflow's `publish-docs` job publishes the site the same way after
every release from `main`, once PyPI has it (`smarter-python-release`), so a
release needs no step here. `make sphinx-publish` is for publishing between
releases, e.g. a docs fix. It reads the bucket and distribution from the
Terraform outputs, so it needs `make terraform-init` once, and AWS credentials
for the account. The user publishes; publish yourself only when asked.

## The site's AWS resources (`terraform/docs/`)

Everything is in Terraform; never change these resources by hand or with the
aws cli:

- an ACM certificate (us-east-1), validated by a Route53 record;
- a **private** S3 bucket named after the domain (us-east-2): all public
  access blocked, ACLs disabled, readable only by the distribution (OAC and
  the bucket policy);
- a CloudFront distribution: HTTPS only, the managed CachingOptimized policy,
  `404.html` for missing pages (S3 answers 403 for them), HTTP/2 and 3, IPv6;
- A and AAAA alias records in the `smarter.sh` zone;
- the `smarter-python-docs-publisher` role that the Release workflow's `docs`
  environment assumes, allowed only to sync the bucket and invalidate the
  distribution (`github_actions.tf`). It trusts GitHub's OIDC provider,
  which is one per account and shared by every repository's stack, so this
  stack only reads it (`data "aws_iam_openid_connect_provider"`).

```console
make terraform-init    # once: the S3 backend (state key smarter-python/docs/terraform.tfstate)
make terraform-plan    # writes terraform/docs/tfplan: read it before applying
make terraform-apply   # applies exactly that plan
```

The state bucket's name contains the AWS account id, so `make terraform-init`
reads it from the caller's credentials. `make terraform-plan` also passes it as
the optional `aws_account_id` guard; plain `terraform` uses `AWS_PROFILE`'s
account without the guard. Never write
an account id, or a distribution id, into this public repository. Run
`terraform -chdir=terraform/docs fmt` and `validate` after editing (CI runs
both), and apply only a plan the user has seen: these are live, billable
resources in a shared account and DNS zone.

### Rules for these stacks

These are what went wrong before; each one was found the hard way.

- **Plain `terraform` must work.** `cd terraform/docs && terraform plan` with
  only `AWS_PROFILE` set must not prompt for anything. Terraform signs in as
  the profile's account; never add a required variable that only `make` can
  fill (an `aws_account_id` with no default made a bare `terraform apply`
  stop at a prompt). The account id is needed only for the state bucket's
  name, at `make terraform-init`. An account guard, if any, is an optional
  variable (`default = null`, and
  `allowed_account_ids = var.aws_account_id == null ? null : [var.aws_account_id]`).
- **Read account-wide singletons, never create them.** GitHub's OIDC
  provider (`token.actions.githubusercontent.com`, one per account), the
  `smarter.sh` hosted zone and the state bucket are shared by every
  repository's stack. A stack reads them with a `data` source. Creating one
  fails with `EntityAlreadyExists` (409) in an account that has it, and a
  stack that owns one breaks every other repository when it is destroyed.
  To hand off one that a stack already owns, switch to the `data` source and
  add a `removed { from = ... lifecycle { destroy = false } }` block; the plan
  must say "will no longer be managed by Terraform, but will not be
  destroyed". Nothing manages the OIDC provider now; it is left in place.
- **Look in AWS before writing a stack.** Check with read-only `aws` calls
  whether the bucket, distribution, certificate, records or role already
  exist. Existing resources are adopted with `import` blocks and a
  configuration that describes them as they are, until the plan shows imports
  and no change to anything live, and no destroys. Compute import ids from
  `data` sources (e.g. a certificate's ARN from `data "aws_acm_certificate"`)
  so that no account id is written into the repository.
- **Plan before you hand it over.** After any change, run `terraform plan`
  yourself with the user's profile (it only reads) and read it: a stack that
  validates can still fail at apply. Never leave a stale `tfplan` behind.
- **When the user's apply fails, fix the stack.** Don't explain why it was
  run "wrong" or offer workarounds; the stack is what must work.
