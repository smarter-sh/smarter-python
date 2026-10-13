"""
Models of Smarter Application Manifests (SAM): the YAML documents that declare every Smarter resource.

A manifest has the same four sections as a Kubernetes manifest: ``apiVersion``, ``kind``,
``metadata`` and ``spec``. ``describe`` adds a read-only ``status``. The shape of ``spec`` depends on
the kind and the platform's version, so it is a JSON object here. The platform publishes the
complete JSON Schema of each kind: see :meth:`smarter.resources.manifests.Manifests.json_schema`.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import yaml
from pydantic import Field

from smarter.core.exceptions import SmarterValueError
from smarter.core.typing import SmarterJsonObjectType

from .base import SmarterCamelModel, SmarterModel

if TYPE_CHECKING:
    from .sam.base import SAMModel


SMARTER_API_VERSION = "smarter.sh/v1"
"""The ``apiVersion`` of every Smarter manifest."""


class ManifestMetadata(SmarterModel):
    """A manifest's ``metadata``: the resource's name, and descriptive information about it."""

    name: str = Field(..., description="The resource's name, unique per account and kind, in snake_case.")
    description: Optional[str] = None
    version: Optional[str] = Field(None, description="The resource's semantic version, e.g. 1.0.0.")
    tags: list[str] = []
    annotations: list[SmarterJsonObjectType] = Field(
        default_factory=list, description="Key-value pairs, as a list of single-key objects."
    )


class Manifest(SmarterModel):
    """
    A Smarter Application Manifest.

    .. code-block:: python

        manifest = Manifest.from_yaml(open("llmclient.yaml").read())
        manifest.metadata.name
        manifest.spec["config"]["provider"]
    """

    apiVersion: str = SMARTER_API_VERSION
    kind: str = Field(..., description="The resource kind, e.g. LLMClient. See Smarter.kinds().")
    metadata: ManifestMetadata
    spec: SmarterJsonObjectType = Field(default_factory=dict, description="The resource's specification.")
    status: Optional[SmarterJsonObjectType] = Field(None, description="Read-only state, returned by describe.")

    @classmethod
    def from_yaml(cls, text: str) -> "Manifest":
        """
        Parse a manifest from YAML (or JSON) text.

        :param text: The manifest's text.
        :returns: The manifest.
        :raises SmarterValueError: If the text is not a YAML object.
        """
        try:
            document = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise SmarterValueError(f"The manifest is not valid YAML: {e}") from e
        if not isinstance(document, dict):
            raise SmarterValueError("A manifest must be a YAML object with apiVersion, kind, metadata and spec.")
        return cls.model_validate(document)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Manifest":
        """
        Read a manifest from a YAML or JSON file.

        :param path: The file's path.
        :returns: The manifest.
        """
        return cls.from_yaml(Path(path).read_text(encoding="utf-8"))

    def to_sam(self) -> "SAMModel":
        """
        The manifest as its kind's typed SAM model, e.g. a :class:`~smarter.models.sam.SAMGuardrail`.

        .. code-block:: python

            guardrail = client.guardrails.describe("pii_redactor").to_sam()
            print(guardrail.spec.config.action)

        :returns: The typed manifest.
        :raises SmarterValueError: If the SDK has no model of the manifest's kind.
        :raises pydantic.ValidationError: If the manifest does not match its kind's model.
        """
        from .sam import SAM_MODELS  # pylint: disable=import-outside-toplevel

        model = SAM_MODELS.get(self.kind)
        if model is None:
            raise SmarterValueError(f"The SDK has no SAM model of the {self.kind} kind.")
        return model.model_validate(self.model_dump(mode="json", exclude={"status"} if self.status is None else None))

    def to_yaml(self) -> str:
        """
        The manifest as YAML text, without its read-only ``status``, ready to apply.

        :returns: The YAML text.
        """
        document = self.model_dump(mode="json", exclude_none=True, exclude={"status"})
        return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


class ManifestListTitle(SmarterModel):
    """A column of a ``get`` result: the field's name, and its Django field type."""

    name: str
    type: str


class ManifestListData(SmarterModel):
    """The table of a ``get`` result."""

    titles: list[ManifestListTitle] = []
    items: list[SmarterJsonObjectType] = []


class ManifestListMetadata(SmarterModel):
    """The ``metadata`` of a ``get`` result."""

    count: int = 0


class ManifestList(SmarterModel):
    """
    The result of ``get``: the resources of one kind, as a table.

    ``data.items`` are the rows, and ``data.titles`` their columns. The columns depend on the kind.
    """

    apiVersion: str = SMARTER_API_VERSION
    kind: str
    name: Optional[str] = None
    metadata: ManifestListMetadata = Field(default_factory=ManifestListMetadata)
    data: ManifestListData = Field(default_factory=ManifestListData)

    @property
    def items(self) -> list[SmarterJsonObjectType]:
        """The rows."""
        return self.data.items

    @property
    def names(self) -> list[str]:
        """The names of the resources: each row's ``name``, or its ``username`` for the User kind."""
        names = []
        for item in self.data.items:
            name = item.get("name", item.get("username"))
            if name is not None:
                names.append(str(name))
        return names


class KindInfo(SmarterCamelModel):
    """A resource kind that the platform supports, as ``/api/v1/cli/resources/`` describes it."""

    singular: str = Field(..., alias="Singular")
    plural: str = Field(..., alias="Plural")
    api_kind: str = Field(..., alias="APIKind", description="The kind, as it appears in a manifest.")
    display: Optional[str] = Field(None, alias="Display")
    display_plural: Optional[str] = Field(None, alias="DisplayPlural")
    deployable: bool = Field(False, alias="Deployable", description="True if the kind can be deployed.")


__all__ = [
    "KindInfo",
    "Manifest",
    "ManifestList",
    "ManifestListData",
    "ManifestListMetadata",
    "ManifestListTitle",
    "ManifestMetadata",
    "SMARTER_API_VERSION",
]
