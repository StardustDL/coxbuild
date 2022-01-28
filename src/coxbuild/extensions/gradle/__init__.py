from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import group, run, task

from .. import ProjectSettings, withProject

grouped = group("gradle")


@grouped
@withProject
@task
def build(path: Path | None = None, *, project: ProjectSettings):
    run(["gradle", "build"], cwd=path or project.src)


@grouped
@withProject
@task
def test(path: Path | None = None, *, project: ProjectSettings):
    run(["gradle", "test"], cwd=path or project.test)
