from pathlib import Path

from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run, task

from . import grouped
from .package import hasPackages, upgradePackages

subgrouped = group("format")


@grouped
@subgrouped
@precond(lambda: not hasPackages({"autopep8": "*", "isort": "*"}))
@task
def restore():
    """Restore Python format tools."""
    upgradePackages("autopep8", "isort")


@grouped
@subgrouped
@depend(restore)
@task
def autopep8(path: Path | None = None):
    """Use autopep8 to format Python code."""
    run(["autopep8", "-r", "--in-place", str(path or get_working_directory())])


@grouped
@subgrouped
@depend(restore)
@task
def isort(path: Path | None = None):
    """Use isort to format Python imports."""
    for file in (path or get_working_directory()).glob("**/*.py"):
        if file.is_dir():
            continue
        run(["isort", str(file)])


@grouped
@subgrouped
@depend(autopep8, isort)
@task
def format():
    """Format Python code."""
    pass
