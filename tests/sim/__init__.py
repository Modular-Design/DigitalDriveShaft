import pytest

try:
    from ansys.mapdl.core import Mapdl
except ImportError:
    pytest.skip("skipping simulation tests", allow_module_level=True)
