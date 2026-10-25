Quickstart
==========

Point the SDK at your platform with environment variables, or pass the same values as arguments
to ``Smarter(...)``. If you have run the Smarter CLI's ``smarter configure``, the SDK reads its
configuration file and needs neither. See :doc:`guide/configuration`.

.. code-block:: console

    $ export SMARTER_API_KEY="your 64-character Smarter api key"
    $ export SMARTER_BASE_URL="https://platform.example.com"   # or http://localhost:9357

Prompt an LLMClient
-------------------

.. code-block:: python

    from smarter import Smarter

    client = Smarter()

    llmclient = client.llm_clients.find("customer_support")
    response = client.llm_clients.prompt(llmclient.id, "Where is my order #1234?")
    print(response.text)

Apply a manifest
----------------

.. code-block:: python

    client.manifests.apply("pii-redactor.yaml")                    # create or update
    manifest = client.guardrails.describe("pii_redactor")          # read it back
    guardrail = manifest.to_sam()                                  # as a typed SAMGuardrail
    print(guardrail.spec.config.action)
    client.guardrails.delete("pii_redactor")

Chat, and stream a prompt's progress
------------------------------------

.. code-block:: python

    chat = client.llm_clients.chat(llmclient.id)
    print(chat.send("What is 2 to the 10th power?").text)
    print(chat.send("And divided by 4?").text)

    with chat.stream("Now take its square root.") as stream:
        for event in stream:
            print("...", event.message)     # e.g. "Calling tool calculator"
        print(stream.response.text)

Handle errors
-------------

.. code-block:: python

    from smarter import NotFoundError, SmarterError

    try:
        client.manifests.describe("LLMClient", "no_such_client")
    except NotFoundError as e:
        print(e.status_code, e.message, e.error_class)
    except SmarterError as e:
        print("something else went wrong:", e)

The :doc:`User Guide <guide/configuration>` covers each of these in depth.
