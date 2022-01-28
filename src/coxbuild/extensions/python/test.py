from pathlib import Path

from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run, task

from .. import ProjectSettings, withProject
from . import grouped
from .package import hasPackages, upgradePackages

subgrouped = group("test")


@grouped
@subgrouped
@precond(lambda: not hasPackages({"pytest": "*",  "pytest-asyncio": "*", "pytest-cov": "*", "coverage": "*"}))
@task
def restore():
    """Restore Python test tools."""
    upgradePackages("pytest", "pytest-asyncio", "coverage", "pytest-cov")


@grouped
@subgrouped
@withProject
@depend(restore)
@task
def pytest(src: Path | None = None, test: Path | None = None, *, project: ProjectSettings):
    """Use pytest to test Python code."""
    run(["pytest", "--cov-report=term-missing",
        "--cov-report=html", f"--cov={str(src or project.src)}"], cwd=str(test or project.test))


@grouped
@subgrouped
@depend(pytest)
@task
def test():
    """Test Python code."""
    pass
