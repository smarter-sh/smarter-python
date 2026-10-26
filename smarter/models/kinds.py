"""
The SAM manifest kinds, and the order in which to apply a set of manifests.

:class:`SAMKinds` is defined in `smarter-types <https://docs.smarter-types.smarter.sh/>`__, the package
that the SDK shares with the Smarter platform, and is re-exported here, so that it is the platform's
own definition of which kinds exist.

SAM resources refer to one another by name, so a set of manifests, e.g. a repository of them, must
be applied in an order where every resource comes after the resources that it names:

.. code-block:: python

    from pathlib import Path

    from smarter import Manifest, SAMKinds, Smarter

    manifests = [Manifest.from_file(path) for path in Path("manifests").rglob("*.yaml")]
    with Smarter() as client:
        for manifest in sorted(manifests, key=lambda m: SAMKinds.apply_rank(m.kind)):
            print(client.manifests.apply(manifest).message)
"""

from smarter_types import SAMKinds

__all__ = ["SAMKinds"]
