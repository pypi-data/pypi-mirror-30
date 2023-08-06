import os
from . import utils
from . import main

def find_path():
    """Find the location of package in any given file system."""
    __dir_path__ = os.path.dirname(os.path.realpath(__file__))
    return __dir_path__

with open(os.path.join(find_path(), '__version__')) as f:
    __version__ = f.read().strip()
