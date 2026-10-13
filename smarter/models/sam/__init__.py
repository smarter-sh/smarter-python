"""
Typed models of every SAM (Smarter Application Manifest) kind, generated from the Smarter platform's JSON Schemas.

Each model describes a complete manifest of its kind: ``apiVersion``, ``kind``, ``metadata``,
``spec`` and the read-only ``status``. Use them to build manifests in code, with your editor's
completion and Pydantic's validation, or to read a described manifest with typed fields:

.. code-block:: python

    from smarter.models.sam import SAMGuardrail, sam_model

    manifest = client.guardrails.describe("pii_redactor")
    guardrail = manifest.to_sam()                  # a SAMGuardrail
    print(guardrail.spec.config.action)

The models keep fields that they don't declare, so that a manifest of a newer platform still
parses. The platform's own models also enforce business rules that a JSON Schema can't express:
validate a manifest with :meth:`smarter.resources.manifests.Manifests.validate` before you rely on it.

Do not edit: run ``scripts/generate_sam_models.py``.
"""

from .account import SAMAccount
from .apiconnection import SAMApiConnection
from .apiplugin import SAMApiPlugin
from .base import SAMModel
from .budget import SAMBudget
from .customdomain import SAMCustomDomain
from .guardrail import SAMGuardrail
from .imagesearchplugin import SAMImageSearchPlugin
from .llmclient import SAMLLMClient
from .llmhost import SAMLLMHost
from .llmhostcompute import SAMLLMHostCompute
from .mcpclient import SAMMCPClient
from .orchestrator import SAMOrchestrator
from .plugin import SAMPlugin
from .prompt import SAMPrompt
from .provider import SAMProvider
from .proxy import SAMProxy
from .secret import SAMSecret
from .skillplugin import SAMSkillPlugin
from .smarterauthtoken import SAMSmarterAuthToken
from .sqlconnection import SAMSqlConnection
from .sqlplugin import SAMSqlPlugin
from .user import SAMUser
from .vectorsearch import SAMVectorsearch
from .vectorstore import SAMVectorstore
from .websearchplugin import SAMWebsearchPlugin

SAM_MODELS: dict[str, type[SAMModel]] = {
    "Account": SAMAccount,
    "ApiConnection": SAMApiConnection,
    "ApiPlugin": SAMApiPlugin,
    "Budget": SAMBudget,
    "CustomDomain": SAMCustomDomain,
    "Guardrail": SAMGuardrail,
    "ImageSearchPlugin": SAMImageSearchPlugin,
    "LLMClient": SAMLLMClient,
    "LLMHost": SAMLLMHost,
    "LLMHostCompute": SAMLLMHostCompute,
    "MCPClient": SAMMCPClient,
    "Orchestrator": SAMOrchestrator,
    "Plugin": SAMPlugin,
    "Prompt": SAMPrompt,
    "Provider": SAMProvider,
    "Proxy": SAMProxy,
    "Secret": SAMSecret,
    "SkillPlugin": SAMSkillPlugin,
    "SmarterAuthToken": SAMSmarterAuthToken,
    "SqlConnection": SAMSqlConnection,
    "SqlPlugin": SAMSqlPlugin,
    "User": SAMUser,
    "Vectorsearch": SAMVectorsearch,
    "Vectorstore": SAMVectorstore,
    "WebsearchPlugin": SAMWebsearchPlugin,
}
"""The model of each kind, by its manifest ``kind``."""


def sam_model(kind: str) -> type[SAMModel]:
    """
    The model of a kind.

    :param kind: The manifest kind, e.g. ``LLMClient``.
    :returns: The model, e.g. :class:`SAMLLMClient`.
    :raises KeyError: If the SDK has no model of the kind.
    """
    return SAM_MODELS[kind]


__all__ = [
    "SAMModel",
    "SAM_MODELS",
    "SAMAccount",
    "SAMApiConnection",
    "SAMApiPlugin",
    "SAMBudget",
    "SAMCustomDomain",
    "SAMGuardrail",
    "SAMImageSearchPlugin",
    "SAMLLMClient",
    "SAMLLMHost",
    "SAMLLMHostCompute",
    "SAMMCPClient",
    "SAMOrchestrator",
    "SAMPlugin",
    "SAMPrompt",
    "SAMProvider",
    "SAMProxy",
    "SAMSecret",
    "SAMSkillPlugin",
    "SAMSmarterAuthToken",
    "SAMSqlConnection",
    "SAMSqlPlugin",
    "SAMUser",
    "SAMVectorsearch",
    "SAMVectorstore",
    "SAMWebsearchPlugin",
    "sam_model",
]
