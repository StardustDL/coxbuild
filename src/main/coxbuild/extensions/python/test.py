from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run

from . import Settings, task
from .package import hasPackages, upgradePackages

task = group("test", task)


@precond(lambda: not hasPackages({"pytest": "*",  "pytest-asyncio": "*", "pytest-cov": "*", "coverage": "*"}))
@task()
def restore():
    """Restore Python test tools."""
    upgradePackages("pytest", "pytest-asyncio", "coverage", "pytest-cov")


@depend(restore)
@task()
def pytest():
    """Use pytest to test Python code."""
    run(["pytest", "--cov-report=term-missing",
        "--cov-report=html", f"--cov={str(Settings.buildSrc)}"])


@depend(pytest)
@task()
def test():
    """Test Python code."""
    pass
