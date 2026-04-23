from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("venticoolpy")
except PackageNotFoundError:
    __version__ = None


from venticoolpy import data
from venticoolpy import constant, model, calculation

