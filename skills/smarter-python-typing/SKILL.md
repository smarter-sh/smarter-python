---
name: smarter-python-typing
description: Use when writing or reviewing Python type annotations in the smarter-python SDK, especially any use of typing.Any, Optional[Any], list[Any], dict[str, Any], or a type construction that repeats. Explains the Python 3.10 syntax that pyupgrade enforces, when Any is honest (and when object is truer), the rules for aliases, the Smarter-prefixed aliases in smarter.core.typing (SmarterJsonType, SmarterJsonObjectType, SmarterIdType, SmarterDictType), and the SDK's own typing traps (a method named list, Literal versus str).
---

# Smarter Python SDK Type Annotations

An annotation is a claim about what a value can be. Readers, type checkers and
the SDK's api reference all take it at its word, and the SDK ships `py.typed`,
so **its users' type checkers** read these annotations too. `Any` makes the
weakest possible claim and turns the type checker off for that value, so it's
only correct when the claim is literally true. This is the platform's rule
(ADR-027 and `../smarter/skills/smarter-python-typing`), applied to the SDK.

## Syntax

- Python 3.10 and newer: `X | None`, `list[str]`, `type[Model]`.
  pyupgrade (`--py310-plus`) rewrites the old forms in annotations; write the
  new ones to begin with.
- In an **expression**, the `typing` form stays: an alias's assignment
  (`SmarterIdType = Union[int, str]`), or a `cast()`. pyupgrade leaves it.
- A **quoted forward reference** stays `Optional["X"]`: `"X" | None` fails at
  runtime unless the module starts with `from __future__ import annotations`
  (see `smarter/core/exceptions.py`).

## When `Any` is acceptable

Only where the value really can be of any type:

- `*args: Any, **kwargs: Any` passed through to someone else's api.
- A **type form**, e.g. the `cast_to` of `SmarterHttpClient.request()`, which may
  be a model, `list[Model]`, or any other type that Pydantic validates.
- Comparison dunders: `def __eq__(self, other: Any) -> bool`.

A value that is only stored, compared or passed on is `object`, not `Any`: it
accepts anything and keeps the checker on, e.g. `json: object` in
`SmarterHttpClient.request()`.

## When `Any` is wrong

If you can list the types, list them:

- **A response.** It is a Pydantic model (ADR-031). A JSON value whose shape
  really is free is `SmarterJsonType`; a JSON object whose fields depend on a
  kind (a manifest's `spec`) is `SmarterJsonObjectType`.
- **`Optional[Any]`** says nothing more than `Any`.
- **`Any` to dodge a circular import.** Import under `if TYPE_CHECKING:` and
  quote the annotation (see `smarter/resources/base.py`, which imports `Smarter`).
- **A return type with a finite set of possibilities.** Write the `Union`.
  If callers must then narrow it, that's the truth; consider splitting the
  method in two.
- **A return type that depends on an argument's type.** Use `@overload`, or a
  `TypeVar`, as `SmarterKindResource` does with `ModelT` in
  `smarter/resources/base.py`.
- **A third-party object whose type you didn't look up**, e.g. an `httpx`
  response. Look it up.
- **`:type ...: Any` or `:rtype: Any` in a docstring.** Keep it in step with
  the annotation.

## Aliases in `smarter.core.typing`

| Alias                   | Means                  | Use for                                                    |
| ----------------------- | ---------------------- | ---------------------------------------------------------- |
| `SmarterJsonType`       | `pydantic.JsonValue`   | any JSON value, e.g. a tool's result or a proxy's response |
| `SmarterJsonObjectType` | `dict[str, JsonValue]` | a JSON object whose shape isn't fixed, e.g. a `spec`       |
| `SmarterIdType`         | `Union[int, str]`      | a resource's id or hashed id                               |
| `SmarterDictType`       | `dict[str, Any]`       | a mapping whose values really can be anything (rare here)  |

They mirror the platform's `smarter.lib.typing`. `smarter.core.typing`
imports only the standard library and pydantic, so that any module can import
it. Keep it that way.

- **Use the alias**, not the construction it stands for.
- **Compose it** at the point of use (`list[SmarterJsonObjectType]`,
  `SmarterDictType | None`). Don't add aliases such as
  `SmarterOptionalDictType`.
- **An alias doesn't make a loose type right.** A dict whose values are all
  strings is `dict[str, str]`, and a response is a Pydantic model.
- **Add an alias here** when a construction that carries meaning recurs across
  modules. Use the platform's name if it has one, else `Smarter<Name>Type`;
  give it a docstring (Sphinx publishes it), add it to `__all__` and to the
  table above, and replace the existing uses in the same change.
- **A construction that belongs to one module's job** gets a module-level
  alias with a docstring there, which other modules import, e.g.
  `QueryParamValue` in `smarter/core/http.py` and `ManifestInput` in
  `smarter/resources/base.py`.
- **Don't alias** single-level generics of concrete types (`list[str]`,
  `dict[str, str]`) or `X | None`. They're as clear as a name would be.

## SDK traps

- **A method named `list` shadows the builtin** in the class body's
  annotations: `def models(self) -> list[ProviderModel]` after `def list(...)`
  fails at import with `'function' object is not subscriptable`. Every module in
  `smarter/resources/` starts with `from __future__ import annotations` for this
  reason. Keep it in new resource modules.
- **`Literal` versus `str`.** A `Literal` of values that the platform may add
  to (a plugin's class, an event's type) breaks the SDK when the platform is
  upgraded. Use `str`, and list the known values in the field's description.
  Keep `Literal` for discriminators and for arguments that the SDK sends (e.g.
  `stage: Literal["input", "output"]`).
- **Timestamps** are `datetime`, not `AwareDatetime`: some platform responses
  carry naive timestamps.

## Checking your work

```console
git diff --name-only -- '*.py' | xargs grep -nE '(: *|-> *|\[)Any\b'
```

For each hit, ask: can I list the types this value can have? If so, list them.
