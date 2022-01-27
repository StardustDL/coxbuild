from pathlib import Path

from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run, task

from .. import projectSettings
from . import grouped, settings
from .package import hasPackages, upgradePackages

grouped = group("test", grouped)


@grouped
@precond(lambda: not hasPackages({"pytest": "*",  "pytest-asyncio": "*", "pytest-cov": "*", "coverage": "*"}))
@task
def restore():
    """Restore Python test tools."""
    upgradePackages("pytest", "pytest-asyncio", "coverage", "pytest-cov")


@grouped
@depend(restore)
@task
def pytest(src: Path | None = None, test: Path | None = None):
    """Use pytest to test Python code."""
    run(["pytest", "--cov-report=term-missing",
        "--cov-report=html", f"--cov={str(src or projectSettings.src)}"], cwd=str(test or projectSettings.test))


@grouped
@depend(pytest)
@task
def test():
    """Test Python code."""
    pass
