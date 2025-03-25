# pylint: disable=duplicate-code
"""Lawrence McDaniel https://lawrencemcdaniel.com."""
import importlib.util
import os
import re
from typing import Dict


MODULE_NAME = "smarter"
HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, MODULE_NAME))

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def load_version() -> Dict[str, str]:
    """Stringify the __version__ module."""
    version_file_path = os.path.join(PROJECT_ROOT, "__version__.py")
    spec = importlib.util.spec_from_file_location("__version__", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.__dict__


VERSION = load_version()


def get_semantic_version() -> str:
    """
    Return the semantic version number.

    Example valid values of __version__.py are:
    0.1.17
    0.1.17-next.1
    0.1.17-next.2
    0.1.17-next.123456
    0.1.17-next-major.1
    0.1.17-next-major.2
    0.1.17-next-major.123456

    Note:
    - pypi does not allow semantic version numbers to contain a dash.
    - pypi does not allow semantic version numbers to contain a 'v' prefix.
    - pypi does not allow semantic version numbers to contain a 'next' suffix.
    """
    version = VERSION["__version__"]
    version = re.sub(r"-next\.\d+", "", version)
    return re.sub(r"-next-major\.\d+", "", version)


def load_readme() -> str:
    """Stringify the README."""
    with open(os.path.join(HERE, "README.md"), encoding="utf8") as f:
        readme = f.read()
    # Replace img src for publication on pypi
    return readme.replace(
        "./doc/",
        "https://github.com/lpm0073/secure-logger/raw/main/doc/",
    )


def load_about() -> Dict[str, str]:
    """Stringify the __about__ module."""
    about: Dict[str, str] = {}
    about_path = os.path.join(PROJECT_ROOT, "__about__.py")
    spec = importlib.util.spec_from_file_location("__about__", about_path)
    about_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(about_module)
    about = {attr: getattr(about_module, attr) for attr in dir(about_module) if not attr.startswith("_")}
    return about


def load_requirements(filename) -> list:
    with open(filename, encoding="utf-8") as f:
        lines = f.read().splitlines()
    # Filter out comments and empty lines
    requirements = [line for line in lines if line and not line.startswith("#")]
    return requirements
