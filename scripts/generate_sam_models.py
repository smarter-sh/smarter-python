"""
Generate the SDK's SAM models from the Smarter platform's committed JSON Schemas.

The platform's SAM (Smarter Application Manifest) models are Pydantic models that depend on Django,
so the SDK cannot import them. The platform commits each kind's JSON Schema, generated from those
models, and an example manifest of each kind, in ``smarter/smarter/apps/api/v1/contract/sam/``.
``scripts/sync-contracts.sh`` copies them into ``tests/data/sam/``. This script:

1. generates ``smarter/models/sam/<kind>.py`` from each kind's schema with
   datamodel-code-generator, on :class:`smarter.models.sam.base.SAMModel`, and
2. writes ``smarter/models/sam/__init__.py``, whose ``SAM_MODELS`` maps each kind to its model.

The tests check that every generated model parses its kind's example manifest.

usage, from the repository root (``make sam-models`` runs both):

    scripts/sync-contracts.sh ../smarter
    python scripts/generate_sam_models.py            # every kind
    python scripts/generate_sam_models.py Guardrail  # only these kinds
"""

import argparse
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
    """Generate the models of the schemas in ``tests/data/sam/``."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kinds", nargs="*", help="only these kinds")
    args = parser.parse_args()
    all_kinds = sorted(path.name.split(".")[0] for path in DATA.glob("*.schema.json"))
    if not all_kinds:
        sys.exit(f"No schemas in {DATA}. Run scripts/sync-contracts.sh first.")
    unknown = sorted(set(args.kinds) - set(all_kinds))
    if unknown:
        sys.exit(f"No schemas of {', '.join(unknown)} in {DATA}.")
    for kind in args.kinds or all_kinds:
        generate(kind)
    # remove the models of kinds that the platform no longer has.
    for module in PACKAGE.glob("*.py"):
        if module.stem not in {"__init__", "base"} | {module_name(kind) for kind in all_kinds}:
            module.unlink()
            print(f"removed {module.relative_to(ROOT)}")
    write_package(all_kinds)


if __name__ == "__main__":
    main()
