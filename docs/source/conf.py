# pylint: disable=invalid-name,redefined-builtin,wrong-import-position
"""
Sphinx configuration of the Smarter Python SDK's documentation, published to https://docs.smarter-python.smarter.sh/.

Build it with ``make sphinx-build``, which treats every warning as an error,
and publish it with ``make sphinx-publish``.
"""

import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
# the repository root, never ./smarter, whose modules (types, http) would shadow the standard library.
sys.path.insert(0, REPO_ROOT)

from smarter import __version__  # noqa: E402

# -- Project ------------------------------------------------------------------

project = "smarter-python"
author = "Lawrence McDaniel"
copyright = f"{date.today().year}, {author}"  # noqa: A001
version = __version__
release = __version__

SITE_URL = "https://docs.smarter-python.smarter.sh/"
GITHUB_URL = "https://github.com/smarter-sh/smarter-python"

# -- General ------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "notfound.extension",
    "sphinx_sitemap",
]

# _templates/footer.html adds The Smarter Project to every page's footer.
templates_path = ["_templates"]
exclude_patterns: list[str] = []
language = "en"

autodoc_typehints = "signature"
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "show-inheritance": True}

# the generated SAM modules each define their own copy of the classes that several kinds share, e.g.
# SAMPluginCommonMetadata, so an unqualified name in their annotations has a target in every module
# that defines it. Sphinx links the first, which documents the same fields.
suppress_warnings = ["ref.python"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://pydantic.dev/docs/validation/latest/", None),
}

# copy only the code, not the prompts of console examples.
copybutton_prompt_text = r"\$ |>>> |\.\.\. "
copybutton_prompt_is_regexp = True

# -- HTML -----------------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = f"smarter-python {__version__}"
html_short_title = "smarter-python"
html_baseurl = SITE_URL
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
    "style_external_links": True,
    "prev_next_buttons_location": "both",
}
# the "Edit on GitHub" link at the top of each page.
html_context = {
    "display_github": True,
    "github_user": "smarter-sh",
    "github_repo": "smarter-python",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}
html_show_sourcelink = False
html_copy_source = False
html_extra_path = ["_extra"]

# sitemap.xml lists every page under the site's root, without a version prefix.
sitemap_url_scheme = "{link}"

# 404.html is served by CloudFront for every missing page, at any depth, so its links are absolute.
notfound_urls_prefix = "/"


# -- The generated SAM models ---------------------------------------------------

GENERATED_SAM_MODULE = re.compile(r"^smarter\.models\.sam\.(?!base\b)\w+\.")


def escape_plain_text(app, what, name, obj, options, lines):  # pylint: disable=unused-argument,too-many-arguments
    """
    Escape the field docstrings of the generated SAM models for reStructuredText.

    Their fields' descriptions come from the platform's JSON Schemas, and are plain text: the ``*``
    of ``models/*`` must not start emphasis. Their classes' docstrings are reStructuredText.
    """
    if what != "attribute" or not GENERATED_SAM_MODULE.match(name):
        return
    for i, line in enumerate(lines):
        line = line.replace("\\", "\\\\")
        for char in ("*", "`", "|"):
            line = line.replace(char, "\\" + char)
        lines[i] = re.sub(r"(\w)_(\W|$)", r"\1\\_\2", line)


def setup(app):
    """Register the docstring hook."""
    app.connect("autodoc-process-docstring", escape_plain_text)
