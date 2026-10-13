"""
Type aliases of the Smarter SDK.

These mirror ``smarter.lib.typing`` in the Smarter platform. This module imports only from the
standard library and pydantic, so that any module of the SDK can import it without an import cycle.
"""

from typing import Any, Union

from pydantic import JsonValue

SmarterDictType = dict[str, Any]
"""A mapping whose values really can be of any type.

Prefer a Pydantic model when the shape is known.
"""

SmarterJsonType = JsonValue
"""A value that is arbitrary JSON: a string, number, boolean, null, or a list or object of them."""

SmarterJsonObjectType = dict[str, JsonValue]
"""A JSON object whose shape is not fixed, e.g. a manifest's ``spec``, whose fields depend on its kind."""

SmarterIdType = Union[int, str]
"""A resource's id: its integer primary key, or its hashed id, e.g. ``rMTAwMDAwNQx``."""

__all__ = ["SmarterDictType", "SmarterIdType", "SmarterJsonObjectType", "SmarterJsonType"]
