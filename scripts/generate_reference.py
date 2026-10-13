"""
Generate the SDK's api reference pages for the Smarter platform's Sphinx documentation.

The SDK's documentation lives in the platform's repository, whose Sphinx build autodocs the
platform's own ``smarter`` package. Both packages are named ``smarter``, so that build can't import
the SDK. This script imports the SDK here, and writes its docstrings as Sphinx ``py:`` domain
directives (``.. py:class::``, ``.. py:method::``, ...) that need no import:

    ../smarter/docs/source/smarter-framework/smarter-python/reference/<module>.rst
    ../smarter/docs/source/smarter-framework/smarter-python/reference/sam/<kind>.rst

The docstrings are reStructuredText, so they render as the platform's own autodoc pages do.

usage, from the repository root:

    python scripts/generate_reference.py [path of a smarter checkout, default ../smarter]
"""

import ast
import importlib
import inspect
import re
import sys
import textwrap
from collections.abc import Iterator
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PAGES = {
    "client": ("The Client", ["smarter.client"]),
    "core": (
        "Configuration, Transport and Errors",
        [
            "smarter.core.conf",
            "smarter.core.exceptions",
            "smarter.core.http",
            "smarter.core.streaming",
            "smarter.core.log",
            "smarter.core.typing",
        ],
    ),
    "resources": (
        "Resources",
        [
            "smarter.resources.base",
            "smarter.resources.manifests",
            "smarter.resources.llmclients",
            "smarter.resources.guardrails",
            "smarter.resources.mcpclients",
            "smarter.resources.vectorstores",
            "smarter.resources.llmhosts",
            "smarter.resources.catalog",
            "smarter.resources.accounts",
            "smarter.resources.history",
            "smarter.resources.providers",
            "smarter.resources.proxies",
        ],
    ),
    "models": (
        "Models",
        [
            "smarter.models.base",
            "smarter.models.manifest",
            "smarter.models.platform",
            "smarter.models.account",
            "smarter.models.llmclient",
            "smarter.models.plugin",
            "smarter.models.guardrail",
            "smarter.models.mcpclient",
            "smarter.models.vectorstore",
            "smarter.models.llmhost",
            "smarter.models.misc",
        ],
    ),
    "contracts": (
        "API Contracts",
        ["smarter.models.chat", "smarter.models.journal", "smarter.models.react"],
    ),
}

HEADER = """..
   Generated from the smarter-python SDK's docstrings by its scripts/generate_reference.py.
   Do not edit: change the docstring in https://github.com/smarter-sh/smarter-python, and regenerate.

"""

PYDANTIC_METHODS = set(dir(BaseModel))


def indent(text: str, level: int = 1) -> str:
    """Text indented for a directive's content."""
    return textwrap.indent(text, "   " * level)


def docstring(obj: object) -> str:
    """An object's own docstring, cleaned, or an empty string."""
    doc = obj.__doc__ if isinstance(obj, (type, property)) or callable(obj) else None
    return inspect.cleandoc(doc) if isinstance(doc, str) else ""


def plain(text: str) -> str:
    """
    Plain text, escaped for reStructuredText.

    Field descriptions, e.g. those of the generated SAM models, come from the platform's schemas,
    and are plain text: a ``*`` in ``v1/models/*`` must not start emphasis.
    """
    text = text.replace("\\", "\\\\")
    for char in ("*", "`", "|"):
        text = text.replace(char, "\\" + char)
    return re.sub(r"(\w)_(\W|$)", r"\1\\_\2", text)


def signature(obj: object, *, drop_self: bool = False) -> str:
    """A callable's signature, without ``self``."""
    try:
        sig = inspect.signature(obj)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "()"
    parameters = list(sig.parameters.values())
    if drop_self and parameters and parameters[0].name in ("self", "cls"):
        parameters = parameters[1:]
    # "type" would resolve to every documented field named type.
    return re.sub(r"\btype\[", "Type[", str(sig.replace(parameters=parameters)))


def module_data(module) -> Iterator[tuple[str, str]]:
    """The module-level names that have a docstring on the line after their assignment."""
    try:
        tree = ast.parse(inspect.getsource(module))
    except (OSError, TypeError):
        return
    body = tree.body
    for node, following in zip(body, body[1:]):
        target: Optional[str] = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        if (
            target
            and not target.startswith("_")
            and isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
            and isinstance(following.value.value, str)
        ):
            yield target, inspect.cleandoc(following.value.value)


def class_members(cls: type) -> Iterator[str]:
    """The directives of a class's own fields, properties and methods."""
    if issubclass(cls, BaseModel):
        for name, field in cls.model_fields.items():
            if name not in cls.__dict__.get("__annotations__", {}):
                continue
            annotation = getattr(field.annotation, "__name__", None) or str(field.annotation)
            annotation = annotation.replace("typing.", "")
            lines = [f".. py:attribute:: {name}", f"   :type: {annotation}"]
            if field.alias and field.alias != name:
                lines.append(f"   :value: alias ``{field.alias}``")
            description = (field.description or "").strip()
            yield "\n".join(lines) + (
                "\n\n" + indent(plain(inspect.cleandoc(description))) if description else ""
            ) + "\n"
    for name, member in cls.__dict__.items():
        if name.startswith("_") or name in PYDANTIC_METHODS and issubclass(cls, BaseModel) and name != "model_config":
            continue
        if name == "model_config":
            continue
        if isinstance(member, (property,)) or type(member).__name__ == "cached_property":
            target = member.fget if isinstance(member, property) else member.func  # type: ignore[attr-defined]
            yield f".. py:property:: {name}\n\n{indent(docstring(target))}\n"
        elif isinstance(member, (staticmethod, classmethod)):
            function = member.__func__
            kind = "staticmethod" if isinstance(member, staticmethod) else "classmethod"
            sig = signature(function, drop_self=kind == "classmethod")
            yield f".. py:method:: {name}{sig}\n   :{kind}:\n\n{indent(docstring(function))}\n"
        elif inspect.isfunction(member):
            yield f".. py:method:: {name}{signature(member, drop_self=True)}\n\n{indent(docstring(member))}\n"


def class_directive(cls: type) -> str:
    """The directive of a class, with its members."""
    bases = ", ".join(f":class:`{base.__module__}.{base.__qualname__}`" for base in cls.__bases__ if base is not object)
    header = f".. py:class:: {cls.__name__}"
    if not issubclass(cls, BaseModel) and "__init__" in cls.__dict__:
        header += signature(cls.__init__, drop_self=True)
    body = []
    if bases:
        body.append(f"Bases: {bases}")
    if docstring(cls):
        body.append(docstring(cls))
    body.extend(class_members(cls))
    return header + "\n\n" + indent("\n\n".join(body)) + "\n"


def module_section(name: str) -> str:
    """A module's section: its docstring, its documented data, functions and classes."""
    module = importlib.import_module(name)
    title = f"``{name}``"
    parts = [title, "-" * len(title), "", f".. py:module:: {name}", ""]
    if module.__doc__:
        parts += [inspect.cleandoc(module.__doc__), ""]
    public = getattr(module, "__all__", None)
    for data_name, doc in module_data(module):
        if public is not None and data_name not in public:
            continue
        parts += [f".. py:data:: {data_name}", "", indent(doc), ""]
    for member_name, member in vars(module).items():
        if member_name.startswith("_") or getattr(member, "__module__", None) != name:
            continue
        if public is not None and member_name not in public:
            continue
        if inspect.isclass(member):
            parts += [class_directive(member), ""]
        elif inspect.isfunction(member):
            parts += [f".. py:function:: {member_name}{signature(member)}", "", indent(docstring(member)), ""]
    return "\n".join(parts)


def write(path: Path, text: str) -> None:
    """Write a page, with one final newline and no trailing whitespace."""
    lines = [line.rstrip() for line in text.splitlines()]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    """Write every reference page, and the index of the SAM models' pages."""
    smarter = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "smarter").resolve()
    target = smarter / "docs" / "source" / "smarter-framework" / "smarter-python" / "reference"
    if not (smarter / "docs" / "source").is_dir():
        sys.exit(f"No smarter checkout at {smarter}")
    for page, (title, modules) in PAGES.items():
        text = HEADER + f"{title}\n{'=' * len(title)}\n\n" + "\n".join(module_section(m) for m in modules)
        write(target / f"{page}.rst", text)

    from smarter.models.sam import SAM_MODELS  # pylint: disable=import-outside-toplevel

    entries = []
    for kind, model in SAM_MODELS.items():
        module = model.__module__
        title = f"SAM{kind}"
        text = HEADER + f"{title}\n{'=' * len(title)}\n\n" + module_section(module)
        write(target / "sam" / f"{module.rsplit('.', 1)[-1]}.rst", text)
        entries.append(f"   sam/{module.rsplit('.', 1)[-1]}")
    base = HEADER + "SAM Models\n==========\n\n" + module_section("smarter.models.sam")
    base += "\n" + module_section("smarter.models.sam.base")
    base += "\n.. toctree::\n   :maxdepth: 1\n   :caption: Kinds\n\n" + "\n".join(entries) + "\n"
    write(target / "sam.rst", base)


if __name__ == "__main__":
    main()
