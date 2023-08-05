name = "sampleproject"
try:
    from ._version import version as __version__
except ImportError:
    __version__ = 'unknown'
from ls.sampleproject.sator6 import SquareBuilder
