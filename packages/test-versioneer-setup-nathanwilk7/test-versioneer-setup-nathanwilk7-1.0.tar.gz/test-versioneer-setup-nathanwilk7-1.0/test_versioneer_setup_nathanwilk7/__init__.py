from .test_versioneer_setup_file import test_versioneer_setup_func

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
