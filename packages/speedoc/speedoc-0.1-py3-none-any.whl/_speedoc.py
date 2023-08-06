#!/usr/bin/env python
"""sphinx meets pydoc."""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import builtins
from collections.abc import Callable
from tempfile import TemporaryDirectory
import importlib
from pathlib import Path
import subprocess
import sys
import types

try:
    import setuptools_scm
    __version__ = setuptools_scm.get_version(  # xref setup.py
        root="../..", relative_to=__file__,
        version_scheme="post-release", local_scheme="node-and-date")
except (ImportError, LookupError):
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution("speedoc").version
    except pkg_resources.DistributionNotFound:
        pass


_templates = {
    "module": """\
.. automodule:: {obj}
   :members:
   :special-members: __init__
   :undoc-members:
""",
    "exception": """\
.. currentmodule:: {mod}

.. autoexception:: {obj}
   :members:
   :special-members: __init__
   :undoc-members:
""",
    "class": """\
.. currentmodule:: {mod}

.. autoclass:: {obj}
   :members:
   :special-members: __init__
   :undoc-members:
""",
    "function": """\
.. currentmodule:: {mod}

.. autofunction:: {obj}
""",
    "data": """\
.. currentmodule:: {mod}

.. autodata:: {obj}
""",
}


def main(argv=None):
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        epilog="""\
Unknown flags are passed to ``python -msphinx``.  For example, numpydoc
rendering can be obtained with ::

    %(prog)s -Dextensions=numpydoc ...

Options to ``man`` can be passed by setting the (standard) ``MANOPT``
environment variable.  For example, justification can be disabled with ::

    MANOPT=--nj %(prog)s ...
""")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s {}".format(__version__))
    parser.add_argument("obj", help="object to document")
    args, rest = parser.parse_known_args(argv)
    if not all(opt.startswith("-") for opt in rest):
        parser.error("only one object can be documented at a time")

    parts = args.obj.split(".")
    mod = obj = builtins
    try:
        for i in range(len(parts)):
            mod = obj = importlib.import_module(".".join(parts[:i + 1]))
    except ImportError:
        for j in range(i, len(parts)):
            obj = getattr(obj, parts[j])

    template = _templates[
        "module" if isinstance(obj, types.ModuleType) else
        "exception" if (isinstance(obj, type)
                        and issubclass(obj, Exception)) else
        "class" if isinstance(obj, type) else
        "function" if isinstance(obj, Callable) else
        "data"  # no support for automethod, autoattribute.
    ]
    with TemporaryDirectory() as tmpdir:
        Path(tmpdir, "conf.py").write_text(r"""\
version = {version!r}

# Force autosummary to be loaded before -Dextensions=..., to allow swapping out
# just napoleon.
import sys
__overrides = sys._getframe(2).f_locals["overrides"]
__required_extensions = "sphinx.ext.autosummary"
__overrides["extensions"] = (
    __required_extensions + "," + __overrides["extensions"]
    if __overrides.get("extensions") else __required_extensions)

# No description, no authors, section 3 ("library calls").
man_pages = [("contents", "{name}", "", "", "3")]

def man_visit_math(self, node):
    from docutils import nodes
    child, = node.children
    self.body.append("$ {{}} $".format(child.replace("\\", "\\\\")))
    raise nodes.SkipNode

def setup(app):
    from sphinx.ext.mathbase import math, displaymath
    app.add_node(math, override=True, man=(man_visit_math, None))
""".format(name=args.obj, version=getattr(obj, "__version__", "")))
        Path(tmpdir, "contents.rst").write_text(
            template.format(mod=mod.__name__, obj=args.obj))
        subprocess.run(
            [sys.executable, "-msphinx", ".", "build", "-bman", "-q",
             "-Dextensions=sphinx.ext.napoleon"] + rest,
            cwd=tmpdir, check=True)
        subprocess.run(["man", "build/{}.3".format(args.obj)], cwd=tmpdir)


if __name__ == "__main__":
    main()
