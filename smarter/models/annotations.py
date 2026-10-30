"""
SAM annotations: the Kubernetes-style map of string keys to string values in a manifest's ``metadata``.

Annotations are SAM's extension point. A client or an integration attaches them to a resource for
its own purposes, e.g. ``acme.com/crm-account-id: A-10042`` to associate an LLMClient with an
account in a CRM. A key is an optional DNS-subdomain prefix that names its owner, then a slash and
a name of one or more slash-separated segments. The prefix ``smarter.sh`` and its subdomains are
reserved for the platform. Values are strings.

Smarter 0.37 and earlier wrote annotations as a list of one-key maps,
``[{"acme.com/crm-account-id": "A-10042"}]``, with values of any scalar type. The platform still
accepts that form on apply, and so does the SDK: :func:`normalize_annotations` turns either form
into the map, converting each value to the string that the platform stores. The platform decides
whether a key is valid, so the SDK doesn't check keys.

.. code-block:: python

    manifest = client.llmclients.describe("stackademy_sql")
    manifest.metadata.annotations["acme.com/crm-account-id"]

    client.manifests.get("LLMClient", annotation="acme.com/crm-account-id=A-10042")
"""

import json
from collections.abc import Sequence
from datetime import date, datetime
from typing import Annotated, Union

from pydantic import BeforeValidator

from smarter.core.typing import SmarterAnnotationsType

AnnotationSelector = Union[str, Sequence[str]]
"""
An annotation selector: one requirement, or several that must all match.

Requirements use the syntax of Kubernetes label selectors: ``key`` (the resource has the key),
``!key`` (it hasn't), ``key=value`` and ``key!=value``. As in Kubernetes, ``key!=value`` also
matches resources without the key.
"""


def annotation_value(value: object) -> str:
    """
    An annotation's value as the string that the platform stores.

    YAML reads unquoted scalars such as ``true``, ``42`` or ``2024-06-15`` as other types, so they
    are converted to the string that was written: booleans to ``true`` or ``false``, dates to ISO
    8601, and ``None`` to an empty string. A list or an object, which older platforms stored, is
    kept as its JSON text, as the platform's own upgrade did.

    :param value: The value.
    :returns: The value as a string.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str)
    return str(value)


def normalize_annotations(value: object) -> object:
    """
    Annotations in either accepted form, as a map of strings to strings.

    Accepts the map, ``{"acme.com/crm-id": "42"}``, and the list of one-key maps of Smarter 0.37 and
    earlier, ``[{"acme.com/crm-id": 42}]``. When a key appears twice in a list, its last value wins.
    ``None`` is an empty map. Any other value is returned as is, for Pydantic to reject.

    .. code-block:: python

        normalize_annotations([{"acme.com/active": True}])  # {"acme.com/active": "true"}

    :param value: The annotations.
    :returns: The map, or the value unchanged if it is neither form.
    :raises ValueError: If an item of a list is not a map.
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(key): annotation_value(item) for key, item in value.items()}
    if isinstance(value, list):
        result: SmarterAnnotationsType = {}
        for item in value:
            if not isinstance(item, dict):
                raise ValueError(f"Each item of a list of annotations must be a key-value map, not {item!r}.")
            result.update((str(key), annotation_value(entry)) for key, entry in item.items())
        return result
    return value


def annotation_selector(selector: AnnotationSelector | None) -> list[str]:
    """
    An annotation selector as the list of its requirements, without blank ones.

    :param selector: One requirement, several, or None.
    :returns: The requirements, each stripped of surrounding whitespace.
    """
    if selector is None:
        return []
    requirements = [selector] if isinstance(selector, str) else list(selector)
    return [requirement.strip() for requirement in requirements if requirement.strip()]


SmarterAnnotations = Annotated[SmarterAnnotationsType, BeforeValidator(normalize_annotations)]
"""A model field of annotations: a map of strings, which also accepts the legacy list.

See :func:`normalize_annotations`.
"""


__all__ = [
    "AnnotationSelector",
    "SmarterAnnotations",
    "annotation_selector",
    "annotation_value",
    "normalize_annotations",
]
