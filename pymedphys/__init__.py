"""Module docstring."""

# pylint: disable = wrong-import-position
# isort: skip

import lazy_import

LAZY_MODULES = ("matplotlib", "numpy", "shapely", "pymssql")

for module_name in LAZY_MODULES:
    lazy_import.lazy_module(module_name)


from . import dicom, electronfactors, mosaiq, mudensity  # isort:skip
from ._data import data_path, zip_data_paths  # isort:skip
from ._delivery import Delivery  # isort:skip
from ._gamma.implementation.shell import gamma_shell as gamma  # isort:skip
from ._trf import read_trf  # isort:skip
from ._version import __version__, version_info  # isort:skip
