"""
The base classes of the SDK's response models.

Every model allows extra fields. The Smarter platform adds fields to its responses in minor
releases, and an SDK that rejected them would break whenever the platform is upgraded. Extra fields
are kept, and are available as attributes and in :meth:`SmarterModel.to_dict`.
"""

import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from smarter.core.typing import SmarterDictType, SmarterJsonObjectType


class SmarterModel(BaseModel):
    """
    The base class of the SDK's models: a Pydantic model that keeps unknown fields.

    Pydantic's ``model_`` namespace isn't protected, because the api has fields such as an LLMHost's
    ``modelTask``, which older Pydantic versions would warn about.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True, protected_namespaces=())

    def to_dict(self) -> SmarterDictType:
        """
        The model as a JSON-compatible dict, with the api's own field names.

        :returns: The fields that the api returned, or that were set.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_unset=True)

    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        The model as JSON text, with the api's own field names.

        :param indent: The indentation, or None for compact JSON.
        :returns: The JSON text.
        """
        return json.dumps(self.to_dict(), indent=indent)


class SmarterCamelModel(SmarterModel):
    """
    A model of a response whose field names are camelCase, e.g. ``hashedId``.

    Its attributes are snake_case (``hashed_id``), and it accepts either spelling.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True, alias_generator=to_camel)


class SmarterUserRef(SmarterCamelModel):
    """The user of a resource's owner."""

    username: str
    email: Optional[str] = None


class SmarterAccountRef(SmarterCamelModel):
    """The account of a resource's owner."""

    account_number: str


class SmarterOwner(SmarterCamelModel):
    """The owner of a resource: its user profile, as the user and the account."""

    user: Optional[SmarterUserRef] = None
    account: Optional[SmarterAccountRef] = None


class SmarterResource(SmarterCamelModel):
    """
    The fields that every Smarter resource shares, as the REST api returns them.

    The api's resources are Django rows with the same metadata as a manifest's ``metadata``: a name,
    description, version, tags and annotations. Each resource's model adds its own fields.
    """

    id: int
    hashed_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    tags: list[str] = []
    annotations: list[SmarterJsonObjectType] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_profile: Optional[SmarterOwner] = None
    can_delete: Optional[bool] = None
    manifest_url: Optional[str] = None
    ready: Optional[bool] = None


__all__ = [
    "SmarterAccountRef",
    "SmarterCamelModel",
    "SmarterModel",
    "SmarterOwner",
    "SmarterResource",
    "SmarterUserRef",
]
