__date__    = '2021-Jun-21'
__authors__ = "M. Newville"
__release_version__ = '0.9.24'

from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("asteval")
except PackageNotFoundError:
    __version__ = __release_version__
