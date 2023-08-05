from pysfm_module import *
import core.pysfm_version

try:
    __version__ = core.pysfm_version.get_version()
except Exception as e:
    __version__ = 'Test version for Local installation. (develop)'

VERSION = __version__

