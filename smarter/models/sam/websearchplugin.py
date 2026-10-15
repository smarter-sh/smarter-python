"""
SAM model of the ``WebsearchPlugin`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field, PositiveInt, confloat, conint, constr

from smarter.models.sam.base import SAMModel


class SAMDependency(SAMModel):
    """A resource that depends on the resource that a manifest describes."""

    kind: str = Field(..., title="Kind")
    """
    Kind[String]: The SAM kind of the resource that depends on this resource, e.g. LLMClient.

    Read only.
    """
    name: str = Field(..., title="Name")
    """
    Name[String]: The name of the resource that depends on this resource.

    Read only.
    """


class SAMPluginCommonMetadata(SAMModel):
    """Smarter API Plugin Manifest - common Metadata class."""

    annotations: None | (
        list[
            dict[
                str,
                (
                    str
                    | int
                    | float
                    | bool
                    | date
                    | datetime
                    | constr(pattern=r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$")
                    | UUID
                    | bytes
                    | list
                    | dict[str, Any]
                ),
            ]
        ]
    ) = Field(None, title="Annotations")
    """
    The manifest annotations.

    Used for storing arbitrary metadata as
                key-value pairs. Example: [{'smarter.sh/test-manifest/project-name': 'Scooby dooby do'}]. The
                key should be a valid url-friendly string. The value accepts
                multi-line string values (YAML block scalars) and various scalar types including
                str, int, float, bool, datetime.date, datetime.datetime, decimal.Decimal, uuid.UUID, bytes, list, dict.
    """
    description: str | None = Field(..., title="Description")
    """
    The description for this resource.

    Be brief. Keep it under 255 characters.
    """
    name: str = Field(..., title="Name")
    """The camelCase name of the manifest resource."""
    pluginClass: str = Field(..., title="Pluginclass")
    """
    The class of the plugin.

    one of: ['api', 'imagesearch', 'skill', 'sql', 'static', 'websearch']
    """
    tags: list[str] | None = Field(None, title="Tags")
    """
    The tags of the manifest.

    Used for generic resource categorization and search. Example: ['tag1', 'tag2']
    """
    version: str | None = Field(..., title="Version")
    """
    The semantic version of the manifest.

    Example: 0.1.0
    """


class SAMPluginCommonSpecPrompt(SAMModel):
    """Smarter API Plugin Manifest - Spec - Prompt class."""

    maxTokens: PositiveInt | None = Field(2048, title="Maxtokens")
    """
    Plugin.spec.prompt.maxTokens[int].

    Optional. The maxTokens of the Plugin. Defaults to 2048. The maximum number of tokens the LLM should generate in the prompt response.
    """
    model: str | None = Field("gpt-6-luna", title="Model")
    """
    Plugin.spec.prompt.model[str] Optional.

    The model of the Plugin. Defaults to gpt-6-luna. Must be one of: ['chat-latest', 'gpt-4.1', 'gpt-4.1-2025-04-14', 'gpt-4.1-mini', 'gpt-4.1-mini-2025-04-14', 'gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-2024-11-20', 'gpt-4o-mini', 'gpt-4o-mini-2024-07-18', 'gpt-5-search-api', 'gpt-5-search-api-2025-10-14', 'gpt-5.2', 'gpt-5.2-2025-12-11', 'gpt-5.4', 'gpt-5.4-2026-03-05', 'gpt-5.4-mini', 'gpt-5.4-mini-2026-03-17', 'gpt-5.5', 'gpt-5.5-2026-04-23', 'gpt-5.6-luna', 'gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-6-astra', 'gpt-6-luna', 'gpt-6-sol', 'gpt-6.1-sol']
    """
    provider: str | None = Field("openai", title="Provider")
    """
    Plugin.spec.prompt.provider[str].

    Optional. The provider of the LLM. Defaults to openai. The provider is the vendor name for the LLM service that will be used to generate the prompt response.
    """
    systemRole: str = Field(..., title="Systemrole")
    """
    Plugin.spec.prompt.systemRole[str].

    Required. The system role that the Plugin will use for the LLM text completion prompt. Be verbose and specific. Ensure that systemRole accurately conveys to the LLM how you want it to use the Plugin data that is returned.
    """
    temperature: confloat(ge=0.0, le=1.0) | None = Field(1.0, title="Temperature")
    """
    Plugin.spec.prompt.temperature[float] Optional.

    The temperature of the Plugin. Defaults to 1.0. Should be between 0 and 1.0. The higher the temperature, the more creative the response. The lower the temperature, the more predictable the response.
    """


class SAMPluginCommonSpecSelector(SAMModel):
    """Smarter API Plugin Manifest - Spec - Selector class."""

    directive: str = Field(..., title="Directive")
    """
    Plugin.spec.selector.directive[str]: Required.

    the kind of selector directive to use for the Plugin. Must be one of: ['search_terms', 'always', 'llm']
    """
    searchTerms: list[str] | None = Field(None, title="Searchterms")
    """
    Plugin.spec.selector.searchTerms[list].

    Optional. The keyword search terms to use when the Plugin directive is 'search_terms'. Keywords are most effective when constrained to 1 or 2 words each and lists are limited to a few dozen items.
    """


class SAMPluginCommonStatus(SAMModel):
    """Smarter API Plugin Manifest - Status class."""

    accountNumber: str = Field(..., title="Accountnumber")
    """
    Plugin.status.account_number: The account owner of this Plugin.

    Read only.
    """
    created: datetime = Field(..., title="Created")
    """
    The date in which this resource was created.

    Read only.
    """
    dependencies: list[SAMDependency] | None = Field(None, title="Dependencies")
    """
    Dependencies[List]: The resources that depend on this resource, and that must be deleted, or stop referring to it, before it can be deleted.

    Lists only the resources that you can read. Read only.
    """
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    Plugin.status.account_number: The Smarter user who created this Plugin.

    Read only.
    """


class WebsearchFetch(SAMModel):
    """Smarter API - WebsearchPlugin.spec.websearchData.fetch: reading web pages by URL."""

    maxCharacters: conint(ge=1000, le=100000) | None = Field(20000, title="Maxcharacters")
    """
    WebsearchPlugin.spec.fetch.maxCharacters[int]: the maximum number of characters of a web page to return, 1000 to 100000.

    Longer pages are truncated.
    """
    respectRobotsTxt: bool | None = Field(True, title="Respectrobotstxt")
    """WebsearchPlugin.spec.fetch.respectRobotsTxt[bool]: whether to obey websites' robots.txt files."""


class Freshness(Enum):
    """
    WebsearchPlugin.spec.search.freshness[str]: by default, restrict results to those published within the last ['day', 'week', 'month', 'year'].

    The LLM can override this per search.
    """

    day = "day"
    week = "week"
    month = "month"
    year = "year"


class Provider(Enum):
    """
    WebsearchPlugin.spec.search.provider[str]: the web search API.

    One of: ['brave', 'tavily']
    """

    brave = "brave"
    tavily = "tavily"


class SafeSearch(Enum):
    """
    WebsearchPlugin.spec.search.safeSearch[str]: adult content filtering.

    One of: ['off', 'moderate', 'strict']
    """

    off = "off"
    moderate = "moderate"
    strict = "strict"


class WebsearchSearch(SAMModel):
    """Smarter API - WebsearchPlugin.spec.websearchData.search: web search, via a web search API."""

    apiKey: str = Field(..., title="Apikey")
    """
    WebsearchPlugin.spec.search.apiKey[str]: the name of the Smarter Secret that contains the web search API's api key.

    The api key itself is never included in the manifest.
    """
    country: str | None = Field(None, title="Country")
    """WebsearchPlugin.spec.search.country[str]: an ISO 3166-1 alpha-2 country code, e.g. us, to localize results."""
    freshness: Freshness | None = Field(None, title="Freshness")
    """
    WebsearchPlugin.spec.search.freshness[str]: by default, restrict results to those published within the last ['day', 'week', 'month', 'year'].

    The LLM can override this per search.
    """
    language: str | None = Field(None, title="Language")
    """WebsearchPlugin.spec.search.language[str]: an ISO 639-1 language code, e.g. en, to localize results."""
    maxResults: conint(ge=1, le=20) | None = Field(5, title="Maxresults")
    """WebsearchPlugin.spec.search.maxResults[int]: the maximum number of results per search, 1 to 20."""
    provider: Provider = Field(..., title="Provider")
    """
    WebsearchPlugin.spec.search.provider[str]: the web search API.

    One of: ['brave', 'tavily']
    """
    safeSearch: SafeSearch | None = Field("moderate", title="Safesearch")
    """
    WebsearchPlugin.spec.search.safeSearch[str]: adult content filtering.

    One of: ['off', 'moderate', 'strict']
    """


class WebsearchData(SAMModel):
    """Smarter API - WebsearchPlugin.spec.websearchData."""

    allowedDomains: list[str] | None = Field(None, title="Alloweddomains")
    """WebsearchPlugin.spec.allowedDomains[list]: if not empty, only these domains, and their subdomains, may be searched and read."""
    blockedDomains: list[str] | None = Field(None, title="Blockeddomains")
    """WebsearchPlugin.spec.blockedDomains[list]: these domains, and their subdomains, are never searched nor read."""
    cacheTtl: conint(ge=0, le=86400) | None = Field(3600, title="Cachettl")
    """
    WebsearchPlugin.spec.cacheTtl[int]: seconds to cache search results and web pages.

    0 disables caching.
    """
    fetch: WebsearchFetch | None = None
    """WebsearchPlugin.spec.fetch[obj]: enables reading web pages by URL."""
    search: WebsearchSearch | None = None
    """
    WebsearchPlugin.spec.search[obj]: enables web search.

    Requires a web search API key.
    """
    timeout: conint(ge=1, le=60) | None = Field(15, title="Timeout")
    """WebsearchPlugin.spec.timeout[int]: seconds to wait for each web request, 1 to 60."""


class SAMWebsearchPluginSpec(SAMModel):
    """Smarter API Manifest - WebsearchPlugin.spec."""

    prompt: SAMPluginCommonSpecPrompt
    """Plugin.spec.prompt[obj]: the LLM prompt engineering to apply to the Plugin."""
    selector: SAMPluginCommonSpecSelector
    """Plugin.spec.selector[obj]: the selector logic to use for the Plugin."""
    websearchData: WebsearchData
    """WebsearchPlugin.spec.websearchData[obj]: the web search and web fetch configuration of the WebsearchPlugin."""


class SAMWebsearchPlugin(SAMModel):
    """Smarter API Manifest - WebsearchPlugin Model."""

    apiVersion: str = Field(..., title="Apiversion")
    """
    ApiVersion[String]: Required.

    The API version of the AbstractSAMBase.
    """
    kind: str = Field(..., title="Kind")
    """
    Kind[String]: Required.

    The kind of resource described by the manifest.
    """
    metadata: SAMPluginCommonMetadata
    """Plugin.metadata[obj]: Required, the Plugin metadata."""
    spec: SAMWebsearchPluginSpec
    """WebsearchPlugin.spec[obj]: Required, the WebsearchPlugin specification."""
    status: SAMPluginCommonStatus | None = None
    """
    Plugin.status[obj]: Optional, Read-only.

    Stateful status information about the Plugin.
    """
