"""The base class of the generated SAM models."""

import yaml
from pydantic import ConfigDict, model_validator

from smarter.models.annotations import normalize_annotations
from smarter.models.base import SmarterModel


class SAMModel(SmarterModel):
    """
    The base class of the generated SAM models: a :class:`~smarter.models.base.SmarterModel`, which keeps unknown fields.

    Its fields keep the manifest's own names, e.g. ``apiVersion`` and ``recordLocator``.

    Its regular expressions use Python's ``re``, because the platform's schemas include patterns
    with look-ahead (e.g. Pydantic's own pattern of a ``Decimal``), which Pydantic's default engine
    doesn't support. The generated fields' docstrings, which come from the platform's field
    descriptions, are their Pydantic descriptions too (``use_attribute_docstrings``).
    """

    model_config = ConfigDict(
        extra="allow", populate_by_name=True, regex_engine="python-re", use_attribute_docstrings=True
    )

    @model_validator(mode="before")
    @classmethod
    def _legacy_annotations(cls, data: object) -> object:
        """
        Accept a metadata's annotations in the list form of Smarter 0.37 and earlier, as the platform does.

        The platform's schemas describe only the map, so the generated ``annotations`` fields are maps.
        A list of one-key maps, and values that YAML read as booleans, numbers or dates, are converted
        to it. See :func:`smarter.models.annotations.normalize_annotations`.

        :param data: The model's input, before validation.
        :returns: The input, with its annotations as a map of strings.
        """
        if isinstance(data, dict) and "annotations" in cls.model_fields:
            annotations = data.get("annotations")
            if isinstance(annotations, (list, dict)):
                data = {**data, "annotations": normalize_annotations(annotations)}
        return data

    def to_manifest_dict(self) -> dict:
        """
        The manifest as a dict, without its read-only ``status``, ready to apply.

        :returns: The manifest.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_none=True, exclude={"status"})

    def to_yaml(self, status: bool | None = False) -> str:
        """
        The manifest as YAML text.

        :param status: True to include the read-only ``status``.
        :returns: The YAML text.
        """
        document = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        if not status:
            document.pop("status", None)
        return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


__all__ = ["SAMModel"]
