from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import group, run, task

from .. import ProjectSettings, withProject

grouped = group("nodejs")


@grouped
@withProject
@task
def restore(path: Path | None = None, *, project: ProjectSettings):
    """Restore npm packages (ci)."""
    run(["npm", "ci"], cwd=path or project.src, retry=3)


@grouped
@withProject
@task
def build(path: Path | None = None, *, project: ProjectSettings):
    """Build npm project."""
    run(["npm", "run", "build"], cwd=path or project.src)


@grouped
@withProject
@task
def dev(path: Path | None = None, *, project: ProjectSettings):
    """Run dev script."""
    run(["npm", "run", "dev"], cwd=path or project.src)


@grouped
@withProject
@task
def serve(path: Path | None = None, *, project: ProjectSettings):
    """Run serve script."""
    run(["npm", "run", "serve"], cwd=path or project.src)
