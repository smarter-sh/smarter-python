"""Models of the platform's own endpoints: ``whoami``, ``version`` and ``status``."""

from pydantic import Field

from smarter.core.typing import SmarterJsonObjectType

from .account import Account, User
from .base import SmarterCamelModel, SmarterModel


class WhoAmI(SmarterModel):
    """The owner of the api key: the user, their account, and the platform's environment."""

    user: User
    account: Account
    environment: str | None = Field(None, description="The platform's environment, e.g. local or prod.")


class ApiVersion(SmarterModel):
    """The platform's version, and the versions of its main Python packages."""

    version: str = Field(..., description="The Smarter platform's semantic version.")
    python: dict[str, str | None] = Field(default_factory=dict, description="Python package versions, by package.")


class CliVersion(SmarterModel):
    """The version of the smarter cli that the platform recommends."""

    version: str | None = None


class PlatformVersion(SmarterModel):
    """The response of ``version``."""

    api: ApiVersion
    cli: CliVersion | None = None


class PlatformStatus(SmarterCamelModel):
    """
    The response of ``status``: the state of the platform's infrastructure and compute.

    The sections' contents depend on how the platform is hosted, so they are JSON objects.
    """

    infrastructures: SmarterJsonObjectType = Field(default_factory=dict)
    compute: SmarterJsonObjectType = Field(default_factory=dict)


__all__ = ["ApiVersion", "CliVersion", "PlatformStatus", "PlatformVersion", "WhoAmI"]
