"""
Lawrence McDaniel https://lawrencemcdaniel.com.

smarter-api
"""

from smarter.__version__ import __version__  # noqa: F401


# The app name will be used to define the name of the default plugin root and
# plugin directory. To avoid conflicts between multiple locally-installed
# versions, if it is defined the version suffix will also be appended to the app
# name.
__app__ = "smarter_" + __version__.split("+", maxsplit=1)[0]
__author__ = "Lawrence McDaniel"
__author_email__ = "lpm0073@gmail.com"
__description__ = "smarter-api"
__url__ = "https://github.com/smarter-sh/smarter-python/"
__license__ = "AGPL-3.0-or-later"
__keywords__ = "smarter-api"
