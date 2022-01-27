from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run, task

from .. import projectSettings

grouped = group("gradle")


@grouped
@task
def build(path: Path | None = None):
    run(["gradle", "build"], cwd=path or projectSettings.src)


@grouped
@task
def test(path: Path | None = None):
    run(["gradle", "test"], cwd=path or projectSettings.test)
