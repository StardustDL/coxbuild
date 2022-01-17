import logging
import os
from pathlib import Path

import click

__version__ = "0.0.5"


def get_app_directory() -> Path:
    """Get coxbuild root directory."""
    return Path(os.path.split(__file__)[0])


def get_working_directory() -> Path:
    """Get coxbuild working directory."""
    return Path(os.curdir)
