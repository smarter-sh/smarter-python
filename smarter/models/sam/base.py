"""The base class of the generated SAM models."""

from typing import Optional

import yaml
from pydantic import ConfigDict

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

    def to_manifest_dict(self) -> dict:
        """
        The manifest as a dict, without its read-only ``status``, ready to apply.

        :returns: The manifest.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_none=True, exclude={"status"})

    def to_yaml(self, status: Optional[bool] = False) -> str:
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
