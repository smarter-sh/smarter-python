"""
Guardrails: checks that the platform runs on prompts and on the LLM's replies.

.. code-block:: python

    result = client.guardrails.evaluate(17, "My card is 4111 1111 1111 1111")
    if result.triggered:
        print(result.disposition, result.text)
"""

from __future__ import annotations

from typing import Literal, Optional

from smarter.core.typing import SmarterIdType
from smarter.models.guardrail import Guardrail, GuardrailEvaluation, GuardrailEvents

from .base import SmarterKindResource, resource_id


class Guardrails(SmarterKindResource[Guardrail]):
    """Guardrails: ``/api/v1/guardrails/``, and the manifest api's ``Guardrail`` kind."""

    kind = "Guardrail"
    path = "guardrails/"
    model = Guardrail

    def evaluate(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        text: str,
        *,
        stage: Literal["input", "output"] = "input",
    ) -> GuardrailEvaluation:
        """
        Dry-run a Guardrail on a text, without saving an event.

        :param id: The Guardrail's id or hashed id.
        :param text: The text, e.g. a prompt (``input``) or an LLM's reply (``output``).
        :param stage: The stage to evaluate the text as. The Guardrail must run on it.
        :returns: Whether it triggered, its disposition, and the text after its action.
        :raises BadRequestError: If the text is empty or too long, or the Guardrail does not run on the stage.
        """
        return self._http.request(
            "POST",
            f"{self.path}{resource_id(id)}/evaluate/",
            json={"text": text, "stage": stage},
            cast_to=GuardrailEvaluation,
        )

    def events(
        self,
        id: SmarterIdType,  # pylint: disable=redefined-builtin
        *,
        reviewed: bool | None = None,
        disposition: str | None = None,
    ) -> GuardrailEvents:
        """
        The latest events of a Guardrail that the user owns.

        :param id: The Guardrail's id or hashed id.
        :param reviewed: Only reviewed (True) or unreviewed (False) events.
        :param disposition: Only events of this disposition, e.g. ``blocked``.
        :returns: The events, newest first.
        """
        return self._http.request(
            "GET",
            f"{self.path}{resource_id(id)}/events/",
            params={"reviewed": reviewed, "disposition": disposition},
            cast_to=GuardrailEvents,
        )


__all__ = ["Guardrails"]
