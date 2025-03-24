"""Setup for secure_logger package."""

from setuptools import find_packages, setup

from setup_utils import get_semantic_version  # pylint: disable=import-error
from setup_utils import load_readme


setup(
    name="smarter-api",
    version=get_semantic_version(),
    description="The official Python library for the Smarter platform Api.",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    author="Lawrence McDaniel",
    author_email="lpm0073@gmail.com",
    maintainer="Lawrence McDaniel",
    maintainer_email="lpm0073@gmail.com",
    url="https://github.com/smarter-sh/smarter-api",
    license="AGPLv3",
    license_files=("LICENSE.txt",),
    platforms=["any"],
    packages=find_packages(),
    package_data={
        "smarter": ["*.md"],
    },
    python_requires=">=3.8",
    install_requires=["pydantic>=2.0.0"],
    extras_require={},
    classifiers=[  # https://pypi.org/classifiers/
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
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
        "Source": "https://github.com/smarter-sh/smarter-api",
        "Documentation": "https://pypi.org/project/smarter-api/",
        "Changelog": "https://github.com/smarter-sh/smarter-api/blob/main/CHANGELOG.md",
        "Security": "https://github.com/smarter-sh/smarter-api/blob/main/SECURITY.md",
        "Code of Conduct": "https://github.com/smarter-sh/smarter-api/blob/main/CODE_OF_CONDUCT.md",
        "Tracker": "https://github.com/smarter-sh/smarter-api/issues",
    },
)
