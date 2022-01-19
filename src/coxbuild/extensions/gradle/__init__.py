from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run
from .. import projectSettings

task = group("gradle")


@task()
def build(path: Path | None = None):
    run(["gradle", "build"], cwd=path or projectSettings.src)


@task()
def test(path: Path | None = None):
    run(["gradle", "test"], cwd=path or projectSettings.test)
