"""Setup for smarter package."""

import os
import re
from typing import Dict

from setuptools import find_packages, setup


MODULE_NAME = "smarter"
HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, MODULE_NAME))

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def load_version() -> Dict[str, str]:
    """Parse the __version__.py file to extract the version without importing the package."""
    version_file_path = os.path.join(PROJECT_ROOT, "__version__.py")
    version: Dict[str, str] = {}
    with open(version_file_path, encoding="utf-8") as f:
        for line in f:
            # Match lines like __version__ = "0.1.0"
            match = re.match(r"^__(\w+)__\s*=\s*[\"'](.+?)[\"']$", line)
            if match:
                version[f"__{match.group(1)}__"] = match.group(2)  # Ensure keys like "__version__"
    return version


def load_about() -> Dict[str, str]:
    """Parse the __about__.py file to extract metadata without importing the package."""
    about: Dict[str, str] = {}
    about_path = os.path.join(PROJECT_ROOT, "__about__.py")
    with open(about_path, encoding="utf-8") as f:
        for line in f:
            # Match lines like __author__ = "Author Name"
            match = re.match(r"^__(\w+)__\s*=\s*[\"'](.+?)[\"']$", line)
            if match:
                about[f"__{match.group(1)}__"] = match.group(2)
    return about


VERSION = load_version()
print("VERSION:", VERSION)


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


def load_requirements(filename) -> list:
    with open(filename, encoding="utf-8") as f:
        lines = f.read().splitlines()
    # Filter out comments and empty lines
    requirements = [line.split("#", 1)[0].strip() for line in lines if line and not line.startswith("#")]
    return requirements


README = load_readme()
ABOUT = load_about()

print("Current working directory:", os.getcwd())
print("Detected packages:", find_packages(exclude=["smarter.tests"]))
print("Detected requirements:", load_requirements("requirements/base.txt"))
setup(
    name="smarter-api",
    version=get_semantic_version(),
    description="The official Python library for the Smarter platform Api.",
    long_description=README,
    long_description_content_type="text/markdown",
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    maintainer=ABOUT["__author__"],
    maintainer_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    license=ABOUT["__license__"],
    license_files=("LICENSE.txt",),
    platforms=["any"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "smarter": ["*.md"],
    },
    python_requires=">=3.10",
    install_requires=load_requirements("requirements/base.txt"),
    extras_require={},
    classifiers=[  # https://pypi.org/classifiers/
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    keywords="api, smarter, ai",
    project_urls={
        "Source": "https://github.com/smarter-sh/smarter-python",
        "Documentation": "https://pypi.org/project/smarter-api/",
        "Changelog": "https://github.com/smarter-sh/smarter-python/blob/main/CHANGELOG.md",
        "Security": "https://github.com/smarter-sh/smarter-python/blob/main/SECURITY.md",
        "Code of Conduct": "https://github.com/smarter-sh/smarter-python/blob/main/CODE_OF_CONDUCT.md",
        "Tracker": "https://github.com/smarter-sh/smarter-python/issues",
    },
)
