"""Models of plugins: the tools that an LLMClient's LLM can call."""

from typing import Optional

from pydantic import Field

from .base import SmarterResource


class Plugin(SmarterResource):
    """
    A plugin's metadata.

    Its ``kind`` is the manifest kind, e.g. ``ApiPlugin`` or ``SqlPlugin``, and its ``plugin_class``
    the implementation: api, skill, sql, static, websearch or imagesearch.
    """

    plugin_class: Optional[str] = Field(None, description="api, skill, sql, static, websearch or imagesearch.")
    kind: Optional[str] = Field(None, description="The manifest kind, e.g. ApiPlugin.")


__all__ = ["Plugin"]
