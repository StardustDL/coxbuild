from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run

from . import Settings, task
from .package import hasPackages, upgradePackages

task = group("test", task)


@precond(lambda: not hasPackages({"pytest": "*",  "pytest-asyncio": "*"}))
@task()
def restore():
    """Restore Python test tools."""
    upgradePackages("pytest", "pytest-asyncio")


@depend(restore)
@task()
def pytest():
    """Use pytest to test Python code."""
    run(["pytest", str(get_working_directory())])


@depend(pytest)
@task()
def test():
    """Test Python code."""
    pass
