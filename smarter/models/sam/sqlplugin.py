"""
SAM model of the ``SqlPlugin`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field, PositiveInt, confloat, constr

from smarter.models.sam.base import SAMModel


class ParameterType(Enum):
    """Enum for parameter types."""

    string = "string"
    number = "number"
    integer = "integer"
    boolean = "boolean"
    object = "object"
    array = "array"
    null = "null"


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

    annotations: dict[str, str] | None = Field(
        None,
        examples=[{"acme.com/crm-account-id": "A-10042", "smarter.sh/llmclient/use-case": "customer support"}],
        title="Annotations",
    )
    """
    Annotations, as in Kubernetes: a map of keys to string values that clients and integrations attach to a resource for their own purposes, e.g. to associate it with a resource in another system.

    A key is an optional DNS-subdomain prefix that names its owner, then a slash and a name of one or more slash-separated segments, e.g. 'acme.com/crm-account-id'. The prefix 'smarter.sh' and its subdomains are reserved for the Smarter platform. Values are strings: unquoted YAML scalars such as true, 42 or dates are converted to strings, and structured data belongs in a JSON string. All annotations together are limited to 256 KiB. The list of one-key maps of older manifests, e.g. [{'acme.com/crm-account-id': 'A-10042'}], is also accepted.
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
    systemRole: constr(max_length=32768) = Field(..., title="Systemrole")
    """
    Plugin.spec.prompt.systemRole[str].

    Required. The system role that the Plugin will use for the LLM text completion prompt. Be verbose and specific. Ensure that systemRole accurately conveys to the LLM how you want it to use the Plugin data that is returned. The maximum length is 32768 characters.
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


class TestValue(SAMModel):
    """TestValue class for SqlPlugin and ApiPlugin test values."""

    name: str = Field(..., title="Name")
    """The name of the parameter being tested."""
    value: Any = Field(..., title="Value")
    """The test value for the parameter."""


class Parameter(SAMModel):
    """
    Parameter class for parameterized Plugins.

    This structure is
    intended to match that which is used in the OpenAPI
    function calling specification.
    It is used to define the parameters that a plugin can accept,
    and also for creating the function calling prompt api.
    """

    default: Any | None = Field(None, title="Default")
    """The default value of the parameter, if any."""
    description: str | None = Field(None, title="Description")
    """A description of the parameter."""
    enum: list[str] | None = Field(None, title="Enum")
    """
    A list of allowed values for the parameter.

    Example: ['Celsius', 'Fahrenheit']
    """
    name: str = Field(..., title="Name")
    """The name of the parameter."""
    required: bool | None = Field(False, title="Required")
    """Whether the parameter is required."""
    type: ParameterType
    """The data type of the parameter (one of: string, number, integer, boolean, object, array, null)."""


class SqlData(SAMModel):
    """Smarter API - generic API Connection class."""

    limit: PositiveInt | None = Field(100, title="Limit")
    """
    The maximum number of rows to return from the query.

    Must be a non-negative integer.
    """
    parameters: list[Parameter] | None = Field(None, title="Parameters")
    """
    A JSON dict containing parameter names and data types.

    Example: {'unit': {'type': 'string', 'enum': ['Celsius', 'Fahrenheit'], 'description': 'The temperature unit to use.'}}
    """
    sqlQuery: str = Field(..., title="Sqlquery")
    """The SQL query that this plugin will execute when invoked by the user prompt."""
    testValues: list[TestValue] | None = Field(None, title="Testvalues")
    """
    A JSON dict containing test values for each parameter.

    Example: {'product_id': 1234}.
    """


class SAMSqlPluginSpec(SAMModel):
    """Smarter API SqlData Connection Manifest SqlConnection.spec."""

    connection: str = Field(..., title="Connection")
    """SqlPlugin.spec.selector[obj]: the name of an existing SqlConnector to use for the SqlPlugin."""
    prompt: SAMPluginCommonSpecPrompt
    """Plugin.spec.prompt[obj]: the LLM prompt engineering to apply to the Plugin."""
    selector: SAMPluginCommonSpecSelector
    """Plugin.spec.selector[obj]: the selector logic to use for the Plugin."""
    sqlData: SqlData
    """SqlPlugin.spec.selector[obj]: the SqlData to use for the SqlPlugin."""


class SAMSqlPlugin(SAMModel):
    """Smarter API Manifest - Sql Connection Model."""

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
    spec: SAMSqlPluginSpec
    """SqlPlugin.spec[obj]: Required, the SqlPlugin specification."""
    status: SAMPluginCommonStatus | None = None
    """
    Plugin.status[obj]: Optional, Read-only.

    Stateful status information about the Plugin.
    """
