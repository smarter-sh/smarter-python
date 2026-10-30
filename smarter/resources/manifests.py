"""
The manifest api: the brokered, journaled ``/api/v1/cli/`` endpoints that the ``smarter`` cli uses.

Every resource kind is managed through the same verbs: ``apply``, ``validate``, ``get``,
``describe``, ``delete``, ``deploy``, ``undeploy`` and ``logs``. The kind's broker on the platform
validates the manifest with its Pydantic models and applies its business rules, so this is the
only way that the SDK writes resources.

.. code-block:: python

    from smarter import Smarter

    client = Smarter()
    client.manifests.apply("guardrail.yaml")
    manifest = client.manifests.describe("Guardrail", "pii_redactor")
    client.manifests.delete("Guardrail", "pii_redactor")
"""

from __future__ import annotations

from smarter.core.exceptions import SmarterValueError
from smarter.core.typing import SmarterJsonObjectType, SmarterJsonType
from smarter.models.annotations import AnnotationSelector, annotation_selector
from smarter.models.base import SmarterModel
from smarter.models.journal import SmarterJournaledResponse, SmarterJournalMessage
from smarter.models.manifest import Manifest, ManifestList

from .base import ManifestInput, SmarterAPIResource, to_manifest

CLI_PATH = "cli/"


class ManifestValidation(SmarterModel):
    """The result of validating a manifest, without applying it."""

    valid: bool
    errors: list[SmarterJsonType] = []


def kind_segment(kind: str) -> str:
    """
    A kind as a url path segment.

    :param kind: The manifest kind, e.g. ``LLMClient``.
    :returns: The kind.
    :raises SmarterValueError: If it is empty or not a single path segment.
    """
    text = kind.strip()
    if not text or not text.isidentifier():
        raise SmarterValueError(f"Invalid manifest kind: {kind!r}")
    return text


class Manifests(SmarterAPIResource):
    """The manifest api: apply, validate, get, describe, delete, deploy, undeploy and logs, for any kind."""

    def apply(self, manifest: ManifestInput) -> SmarterJournalMessage:
        """
        Create or update a resource from its manifest.

        The platform compares the manifest with the resource's current state and makes the changes
        that the difference requires.

        :param manifest: The manifest: a :class:`~smarter.models.manifest.Manifest`, a dict, YAML
            text, or the path of a YAML file.
        :returns: The platform's response, whose ``message`` says what was applied.
        :raises BadRequestError: If the platform rejects the manifest.
        """
        parsed = to_manifest(manifest)
        return self._http.request(
            "POST",
            f"{CLI_PATH}apply/",
            json=parsed.model_dump(mode="json", exclude_none=True, exclude={"status"}),
            cast_to=SmarterJournalMessage,
        )

    def validate(self, manifest: ManifestInput) -> ManifestValidation:
        """
        Validate a manifest without applying it.

        :param manifest: The manifest, in any form that :meth:`apply` accepts.
        :returns: Whether it is valid, and its errors.
        """
        parsed = to_manifest(manifest)
        response = self._http.request(
            "POST",
            f"{CLI_PATH}validate/",
            json=parsed.model_dump(mode="json", exclude_none=True, exclude={"status"}),
            cast_to=SmarterJournaledResponse[ManifestValidation],
        )
        return response.data or ManifestValidation(valid=False)

    def get(self, kind: str, name: str | None = None, *, annotation: AnnotationSelector | None = None) -> ManifestList:
        """
        The resources of one kind, as a table.

        .. code-block:: python

            client.manifests.get("LLMClient", annotation="acme.com/crm-account-id=A-10042")
            client.manifests.get("LLMClient", annotation=["acme.com/crm-account-id", "!acme.com/archived"])

        :param kind: The manifest kind, e.g. ``LLMClient``.
        :param name: Only the resource of this name.
        :param annotation: Only the resources that match this annotation selector: one requirement,
            or a list of them that must all match, in the syntax of Kubernetes label selectors
            (``key``, ``!key``, ``key=value``, ``key!=value``). See
            :data:`smarter.models.annotations.AnnotationSelector`.
        :returns: The table: ``.items`` are its rows, and ``.names`` the resources' names.
        :raises BadRequestError: If the annotation selector is invalid.
        """
        response = self._http.request(
            "POST",
            f"{CLI_PATH}get/{kind_segment(kind)}/",
            params={"name": name, "annotation": annotation_selector(annotation)},
            cast_to=SmarterJournaledResponse[ManifestList],
        )
        result = response.data or ManifestList(kind=kind)
        if name is not None:
            # the platform's get ignores the name filter for some kinds, so it is applied here too.
            result.data.items = [item for item in result.data.items if item.get("name") == name]
            result.metadata.count = len(result.data.items)
        return result

    def describe(self, kind: str, name: str) -> Manifest:
        """
        A resource's manifest, with its read-only ``status``.

        :param kind: The manifest kind.
        :param name: The resource's name.
        :returns: The manifest, which :meth:`apply` accepts as is.
        :raises NotFoundError: If the resource does not exist.
        """
        response = self._http.request(
            "POST",
            f"{CLI_PATH}describe/{kind_segment(kind)}/",
            params={"name": name},
            cast_to=SmarterJournaledResponse[Manifest],
        )
        if response.data is None:
            raise SmarterValueError(f"The platform returned no manifest for {kind} {name!r}.")
        return response.data

    def delete(self, kind: str, name: str) -> SmarterJournalMessage:
        """
        Permanently delete a resource.

        :param kind: The manifest kind.
        :param name: The resource's name.
        :returns: The platform's response.
        :raises NotFoundError: If the resource does not exist.
        """
        return self._http.request(
            "POST", f"{CLI_PATH}delete/{kind_segment(kind)}/", params={"name": name}, cast_to=SmarterJournalMessage
        )

    def deploy(self, kind: str, name: str) -> SmarterJournalMessage:
        """
        Deploy a resource, e.g. an LLMClient on its own host name.

        This creates real infrastructure on the platform's cloud, e.g. DNS records, TLS certificates
        and Kubernetes ingresses, which may be billable.

        :param kind: The manifest kind of a deployable resource. See :meth:`smarter.Smarter.kinds`.
        :param name: The resource's name.
        :returns: The platform's response.
        """
        return self._http.request(
            "POST", f"{CLI_PATH}deploy/{kind_segment(kind)}/", params={"name": name}, cast_to=SmarterJournalMessage
        )

    def undeploy(self, kind: str, name: str) -> SmarterJournalMessage:
        """
        Undo a resource's deployment.

        :param kind: The manifest kind.
        :param name: The resource's name.
        :returns: The platform's response.
        """
        return self._http.request(
            "POST", f"{CLI_PATH}undeploy/{kind_segment(kind)}/", params={"name": name}, cast_to=SmarterJournalMessage
        )

    def logs(self, kind: str, name: str) -> SmarterJournaledResponse[SmarterJsonObjectType]:
        """
        A resource's logs.

        :param kind: The manifest kind.
        :param name: The resource's name.
        :returns: The platform's response: its ``message``, and its ``data`` for the kinds that have logs.
        """
        return self._http.request(
            "POST",
            f"{CLI_PATH}logs/{kind_segment(kind)}/",
            params={"name": name},
            cast_to=SmarterJournaledResponse[SmarterJsonObjectType],
        )

    def example_manifest(self, kind: str) -> Manifest:
        """
        A valid example manifest of a kind, to start from.

        :param kind: The manifest kind.
        :returns: The manifest.
        """
        response = self._http.request(
            "POST", f"{CLI_PATH}example-manifest/{kind_segment(kind)}/", cast_to=SmarterJournaledResponse[Manifest]
        )
        if response.data is None:
            raise SmarterValueError(f"The platform returned no example manifest for {kind}.")
        return response.data

    def json_schema(self, kind: str) -> SmarterJsonObjectType:
        """
        The JSON Schema of a kind's manifest, e.g. to validate manifests locally or to generate a form.

        :param kind: The manifest kind.
        :returns: The schema (draft 2020-12).
        """
        response = self._http.request(
            "POST",
            f"{CLI_PATH}json-schema/{kind_segment(kind)}/",
            cast_to=SmarterJournaledResponse[SmarterJsonObjectType],
        )
        return response.data or {}


__all__ = ["CLI_PATH", "ManifestValidation", "Manifests", "kind_segment"]
