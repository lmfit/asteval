__date__    = '2021-Jun-21'
__authors__ = "M. Newville"
__release_version__ = '0.9.24'

try:
    # python >=3.8
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # python <3.8
    # importlib.metadata not available for python 3.7
    from importlib_metadata import version, PackageNotFoundError
try:
    __version__ = version("asteval")
except PackageNotFoundError:
    __version__ = __release_version__
