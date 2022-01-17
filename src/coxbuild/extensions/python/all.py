from . import Settings, settings
from .docs import apidoc
from .format import autopep8, format, isort
from .package import (build, deploy, hasPackages, installBuilt,
                      installedPackages, restore, uninstallBuilt,
                      upgradePackages)
from .test import test
