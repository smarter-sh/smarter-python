"""
The base classes of the SDK's api resources.

Each resource family (LLMClients, Guardrails, ...) is a class whose methods send requests through
the client's :class:`~smarter.core.http.SmarterHttpClient`. Writes go through the manifest api,
exactly as the ``smarter`` cli sends them, so that the platform validates them and applies its
business rules. The REST endpoints are used to read resources, and for actions that the manifest
api has no verb for, such as evaluating a Guardrail or calling an MCP tool.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar, Union

from smarter.core.exceptions import ResourceNotFoundError, SmarterValueError
from smarter.core.http import SmarterHttpClient
from smarter.core.typing import SmarterIdType, SmarterJsonObjectType
from smarter.models.base import SmarterResource
from smarter.models.journal import SmarterJournalMessage
from smarter.models.manifest import Manifest
from smarter.models.sam.base import SAMModel

if TYPE_CHECKING:
    from smarter.client import Smarter

ModelT = TypeVar("ModelT", bound=SmarterResource)

ManifestInput = Union[Manifest, SAMModel, SmarterJsonObjectType, str, Path]
"""A manifest: a :class:`Manifest`, a typed SAM model, a dict, YAML or JSON text, or the path of a YAML or JSON file."""


def resource_id(value: SmarterIdType) -> str:
    """
    A resource id as a url path segment.

    :param value: The resource's integer id, or its hashed id.
    :returns: The id, as text.
    :raises SmarterValueError: If the id is empty, or contains a slash.
    """
    text = str(value).strip()
    if not text or "/" in text:
        raise SmarterValueError(f"Invalid resource id: {value!r}")
    return text


class SmarterAPIResource:
    """
    A group of api operations.

    :param client: The client whose requests the operations send.
    """

    def __init__(self, client: Smarter) -> None:
        self._client = client

    @property
    def _http(self) -> SmarterHttpClient:
        return self._client.http


class SmarterKindResource(SmarterAPIResource, Generic[ModelT]):
    """
    The operations of one resource kind, e.g. Guardrail.

    Subclasses set :attr:`kind`, the manifest kind, and :attr:`path`, the REST list endpoint, and
    :attr:`model`, the model of a resource. They get:

    - ``list()``, ``retrieve()`` and ``find()``, from the REST api, and
    - ``apply()``, ``describe()``, ``delete()``, ``example_manifest()`` and ``json_schema()``, from the
      manifest api.
    """

    kind: ClassVar[str]
    """The manifest kind, e.g. ``Guardrail``."""

    path: ClassVar[str]
    """The REST list endpoint, relative to the api's base url, e.g. ``guardrails/``."""

    model: ClassVar[type[SmarterResource]]
    """The model of one resource."""

    def list(self) -> list[ModelT]:
        """
        Every resource of this kind that the api key's user may read.

        :returns: The resources.
        """
        return self._http.request("GET", self.path, cast_to=list[self.model])  # type: ignore[name-defined]

    def retrieve(self, id: SmarterIdType) -> ModelT:  # pylint: disable=redefined-builtin
        """
        One resource, by its id or hashed id.

        :param id: The resource's integer id, or its hashed id.
        :returns: The resource.
        :raises NotFoundError: If it does not exist, or the user may not read it.
        """
        return self._http.request("GET", f"{self.path}{resource_id(id)}/", cast_to=self.model)

    def find(self, name: str) -> ModelT:
        """
        One resource, by its name.

        :param name: The resource's name.
        :returns: The first resource of that name that the user may read.
        :raises ResourceNotFoundError: If there is none.
        """
        for item in self.list():
            if item.name == name:
                return item
        raise ResourceNotFoundError(f"{self.kind} {name!r} not found.")

    def apply(self, manifest: ManifestInput) -> SmarterJournalMessage:
        """
        Create or update a resource of this kind from its manifest.

        :param manifest: The manifest.
        :returns: The platform's response, whose ``message`` says what was applied.
        :raises SmarterValueError: If the manifest is of another kind.
        """
        parsed = to_manifest(manifest)
        if parsed.kind != self.kind:
            raise SmarterValueError(f"Expected a {self.kind} manifest, not {parsed.kind}.")
        return self._client.manifests.apply(parsed)

    def describe(self, name: str) -> Manifest:
        """
        A resource's manifest, with its read-only ``status``.

        :param name: The resource's name.
        :returns: The manifest.
        """
        return self._client.manifests.describe(self.kind, name)

    def delete(self, name: str) -> SmarterJournalMessage:
        """
        Permanently delete a resource.

        :param name: The resource's name.
        :returns: The platform's response.
        """
        return self._client.manifests.delete(self.kind, name)

    def example_manifest(self) -> Manifest:
        """
        A valid example manifest of this kind, to start from.

        :returns: The manifest.
        """
        return self._client.manifests.example_manifest(self.kind)

    def json_schema(self) -> SmarterJsonObjectType:
        """
        The JSON Schema of this kind's manifest.

        :returns: The schema.
        """
        return self._client.manifests.json_schema(self.kind)


def to_manifest(manifest: ManifestInput) -> Manifest:
    """
    A manifest from any of the forms that the SDK accepts.

    A string that names an existing file is read as a file. Any other string is parsed as YAML.

    :param manifest: The manifest.
    :returns: The parsed manifest.
    :raises SmarterValueError: If it cannot be parsed.
    """
    if isinstance(manifest, Manifest):
        return manifest
    if isinstance(manifest, SAMModel):
        return Manifest.model_validate(manifest.to_manifest_dict())
    if isinstance(manifest, Path):
        return Manifest.from_file(manifest)
    if isinstance(manifest, str):
        if "\n" not in manifest and len(manifest) < 1024 and Path(manifest).is_file():
            return Manifest.from_file(manifest)
        return Manifest.from_yaml(manifest)
    if isinstance(manifest, dict):
        return Manifest.model_validate(manifest)
    raise SmarterValueError(
        f"A manifest must be a Manifest, a dict, YAML text or a path, not {type(manifest).__name__}."
    )


__all__ = [
    "ManifestInput",
    "SmarterAPIResource",
    "SmarterKindResource",
    "resource_id",
    "to_manifest",
]
