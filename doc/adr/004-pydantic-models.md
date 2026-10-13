# ADR-004: Pydantic Models, Forward Compatible

## Status

Accepted

Adapts the platform's [ADR-031: Pydantic Models Over Raw JSON](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/031-pydantic-over-json.rst).

## Context

Every request and response is JSON. The platform models its own JSON with Pydantic (ADR-031). An SDK, unlike the platform, also runs against platforms newer than itself, which add fields and enum values in minor releases.

## Decision

Every response is validated into a Pydantic model, and no annotation is `list[Any]` or `dict[str, Any]`: arbitrary JSON is `SmarterJsonType` (`pydantic.JsonValue`), and a JSON object whose fields depend on a kind is `SmarterJsonObjectType`. Unlike the platform's models of Django rows, **every SDK model allows extra fields**, and a value that the platform may add to (a plugin's class, a progress event's type) is a `str` whose known values are listed in its description, not a `Literal`. Timestamps are `datetime`, because some responses carry naive ones. A response that doesn't match its model raises `APIResponseValidationError`.

## Alternatives Considered

- Raw dicts, as the prototype returned.
- Strict models (`extra="forbid"`, `Literal`), as the platform's own models of its rows are.

## Consequences

- **Positive:**
  - Callers get typed, validated objects, with editor completion.
  - An SDK release keeps working when the platform is upgraded.
- **Negative:**
  - A field that the platform removes or renames still breaks the SDK, as it should.
  - Extra fields aren't typed: they are in `model_extra`.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-003: Writes Go Through the Manifest API](003-writes-through-manifests.md)
- [ADR-005: Mirrored Contracts and Generated SAM Models](005-platform-models.md)
- [ADR-013: Type Annotations](013-type-annotations.md)
