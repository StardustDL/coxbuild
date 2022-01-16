import logging
import os
from pathlib import Path

import click

__version__ = "0.0.4"


def get_app_directory() -> Path:
    return Path(os.path.split(__file__)[0])


def get_working_directory() -> Path:
    return Path(os.curdir)
