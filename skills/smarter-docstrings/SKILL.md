---
name: smarter-docstrings
description: Use when writing or editing Python docstrings in the smarter-python SDK. Docstrings become the SDK's api reference on docs.smarter.sh, so they follow the project's reStructuredText field-list style (:param:, :returns:, :raises:), cross-reference syntax, and the layout that pydocstringformatter enforces.
---

# Smarter Python SDK Docstrings

Docstrings do two jobs: they explain the code to developers, and they become
the SDK's api reference on docs.smarter.sh (`scripts/generate_reference.py`
writes them into the platform's Sphinx docs: see `smarter-sphinx-docs`). Write
for a Python programmer who is new to Smarter. The style is exactly the
platform's, so that the two read as one set of docs.

## Style: reStructuredText field lists

Use reST fields, as the platform does, never Google style (`Args:`):

```python
def evaluate(self, id: SmarterIdType, text: str, *, stage: Literal["input", "output"] = "input") -> GuardrailEvaluation:
    """
    Dry-run a Guardrail on a text, without saving an event.

    :param id: The Guardrail's id or hashed id.
    :param text: The text, e.g. a prompt (``input``) or an LLM's reply (``output``).
    :param stage: The stage to evaluate the text as. The Guardrail must run on it.
    :returns: Whether it triggered, its disposition, and the text after its action.
    :raises BadRequestError: If the text is empty or too long, or the Guardrail does not run on the stage.
    """
```

- `:param name:` for each parameter. Types come from the annotations
  (`sphinx_autodoc_typehints`), so don't repeat them in `:type:`.
- `:returns:` says what the value means, including `None` cases. Use `:rtype:`
  only when there is no annotation.
- `:raises SomeError: when ...` for each exception that callers should handle.
- Indent continuation lines by four spaces.

## Layout (pydocstringformatter enforces it)

- Opening `"""` on its own line, then a **one-line summary that ends with a
  period**, then a blank line, then the body.
- **Keep the summary to one line.** pydocstringformatter puts a period at the
  end of the first line and splits the body after it. A two-line summary is
  mangled into "Queue the task, which." followed by "creates its hosted
  zone...". About 280 docstrings were repaired by putting each whole first
  sentence on the summary line, the only form the formatter leaves alone. Keep
  it that way.
- A body paragraph starts with a capital letter. A body that starts lower case
  usually means a summary was split.
- Use one blank line between paragraphs, and between the body and the fields.

## Content

- **Module docstrings** say what the module is for, and show a short
  `.. code-block:: python` example of using it (see
  `smarter/resources/llmclients.py`).
- **Class docstrings** say what the class represents. A resource class names
  its endpoint and its manifest kind (see `Guardrails`). A client-like class
  lists its constructor's `:param:` fields in the class docstring (see `Smarter`).
- **Methods** cover purpose, parameters, return value, the exceptions a caller
  should handle, and side effects that matter to a caller: **billable** LLM
  requests, and **real infrastructure** that a deploy creates.
- **Model fields** are documented with `Field(..., description="...")`, which
  Pydantic also publishes in the model's JSON Schema. Values that the platform
  may add to are listed in the description, e.g. `"http, sse or stdio."`.
- **Generated code** (`smarter/models/sam/`) takes its docstrings from the
  platform's schema. Fix those in the platform's models, then regenerate.

- Say why, not only what, when the reason isn't obvious. For example: "the
  platform's get ignores the name filter for some kinds, so it is applied here too."
- Be accurate. A docstring that describes old behavior is worse than none. When
  you change behavior, update the docstring in the same edit.

## reST inside docstrings

- `double backticks` for literals: field names, values, commands, and file
  names.
- Cross-references: `:class:`~smarter.models.llmclient.LLMClient``,
`:meth:`~smarter.resources.llmclients.LLMClients.prompt``, and `:func:`,
  `:attr:`, `:mod:`. The `~` shows only the last component. Don't cross-reference
  the platform's modules: the SDK's reference can't resolve them.
- Example code: `.. code-block:: python` (or `json`, `yaml`), followed by a
  blank line and indented content, or `::` at the end of a paragraph.
- Lists need a blank line before them.

## Test docstrings

A test module has a one-line docstring naming what it tests
(`"""Test smarter.resources.guardrails."""`). A test method has a one-line
docstring stating the behavior it proves:
`"""Evaluate() sends the text and stage, and returns the findings."""`.

## Verify

- Run the pre-commit hooks on the file (`smarter-code-quality`): pydocstringformatter
  rewrites docstrings. Review its diff.
- Regenerate the api reference (`python scripts/generate_reference.py`) and
  check its pages as `smarter-sphinx-docs` describes. Don't build the docs.
