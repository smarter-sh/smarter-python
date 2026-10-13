"""
Generate the SDK's SAM models from a running Smarter platform's JSON Schemas.

The platform's SAM (Smarter Application Manifest) models are Pydantic models that depend on Django,
so the SDK cannot import them. The platform publishes each kind's JSON Schema, generated from
those models, at ``/api/v1/cli/json-schema/<Kind>/``. This script:

1. saves each kind's schema, and its example manifest, in ``tests/data/sam/``,
2. generates ``smarter/models/sam/<kind>.py`` from the schema with datamodel-code-generator, on
   :class:`smarter.models.sam.base.SAMModel`, and
3. writes ``smarter/models/sam/__init__.py``, whose ``SAM_MODELS`` maps each kind to its model.

The tests check that every generated model parses its kind's example manifest.

usage, from the repository root, with the SDK's usual configuration (SMARTER_API_KEY, SMARTER_BASE_URL):

    python scripts/generate_sam_models.py
    python scripts/generate_sam_models.py --offline   # regenerate from the saved schemas
"""

import argparse
import json
import subprocess  # nosec B404 - runs datamodel-codegen, with fixed arguments
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tests" / "data" / "sam"
PACKAGE = ROOT / "smarter" / "models" / "sam"

HEADER = '''"""
SAM model of the ``{kind}`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""
'''


def module_name(kind: str) -> str:
    """The module of a kind's model, e.g. ``llmclient`` for ``LLMClient``."""
    return kind.lower()


def fetch(kinds_filter: list[str]) -> list[str]:
    """Save each kind's schema and example manifest from the platform, and return the kinds."""
    sys.path.insert(0, str(ROOT))
    from smarter import Smarter  # pylint: disable=import-outside-toplevel

    DATA.mkdir(parents=True, exist_ok=True)
    with Smarter() as client:
        kinds = [kind.api_kind for kind in client.kinds() if not kinds_filter or kind.api_kind in kinds_filter]
        for kind in kinds:
            schema = client.manifests.json_schema(kind)
            example = client.manifests.example_manifest(kind).model_dump(mode="json", exclude_none=True)
            (DATA / f"{kind}.schema.json").write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
            (DATA / f"{kind}.example.json").write_text(json.dumps(example, indent=2) + "\n")
            print(f"fetched {kind}")
    return kinds


def generate(kind: str) -> None:
    """Generate a kind's module from its saved schema."""
    output = PACKAGE / f"{module_name(kind)}.py"
    subprocess.run(  # nosec B603 B607 - fixed arguments
        [
            "datamodel-codegen",
            "--input",
            str(DATA / f"{kind}.schema.json"),
            "--input-file-type",
            "jsonschema",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--base-class",
            "smarter.models.sam.base.SAMModel",
            "--target-python-version",
            "3.10",
            "--use-schema-description",
            "--use-field-description",
            "--use-standard-collections",
            "--use-double-quotes",
            "--disable-timestamp",
            # the platform's example manifests have naive timestamps, and its describe has aware ones.
            "--output-datetime-class",
            "datetime",
            "--class-name",
            f"SAM{kind}",
            "--output",
            str(output),
        ],
        check=True,
    )
    text = output.read_text()
    # replace the generator's comment header with a module docstring.
    lines = text.splitlines()
    while lines and lines[0].startswith("#"):
        lines.pop(0)
    body = "\n".join(lines).strip("\n")
    output.write_text(HEADER.format(kind=kind) + "\n" + body + "\n")
    print(f"generated {output.relative_to(ROOT)}")


def write_package(kinds: list[str]) -> None:
    """Write the package's ``__init__.py``: its imports and the ``SAM_MODELS`` registry."""
    imports = "\n".join(f"from .{module_name(kind)} import SAM{kind}" for kind in kinds)
    registry = "\n".join(f'    "{kind}": SAM{kind},' for kind in kinds)
    names = "\n".join(f'    "SAM{kind}",' for kind in kinds)
    (PACKAGE / "__init__.py").write_text(f'''"""
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

from .base import SAMModel
{imports}


SAM_MODELS: dict[str, type[SAMModel]] = {{
{registry}
}}
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
{names}
    "sam_model",
]
''')


def main() -> None:
    """Fetch the schemas (unless ``--offline``), and generate the models."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--offline", action="store_true", help="regenerate from the schemas in tests/data/sam/")
    parser.add_argument("kinds", nargs="*", help="only these kinds")
    args = parser.parse_args()
    if args.offline:
        kinds = sorted(path.name.split(".")[0] for path in DATA.glob("*.schema.json"))
    else:
        kinds = fetch(args.kinds)
    for kind in kinds:
        generate(kind)
    all_kinds = sorted(path.name.split(".")[0] for path in DATA.glob("*.schema.json"))
    write_package(all_kinds)


if __name__ == "__main__":
    main()
