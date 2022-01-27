from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run, task

from .. import projectSettings

grouped = group("nodejs")


@grouped
@task
def restore(path: Path | None = None):
    """Restore npm packages (ci)."""
    run(["npm", "ci"], cwd=path or projectSettings.src, retry=3)


@grouped
@task
def build(path: Path | None = None):
    """Build npm project."""
    run(["npm", "run", "build"], cwd=path or projectSettings.src)


@grouped
@task
def dev(path: Path | None = None):
    """Run dev script."""
    run(["npm", "run", "dev"], cwd=path or projectSettings.src)


@grouped
@task
def serve(path: Path | None = None):
    """Run serve script."""
    run(["npm", "run", "serve"], cwd=path or projectSettings.src)
