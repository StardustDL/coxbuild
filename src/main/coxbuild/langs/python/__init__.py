import pathlib

import coxbuild
from coxbuild.schema import config, group, run

task = group("python")
mconfig = config.section("python")


def settings(requirements: pathlib.Path | None = None, buildSrc: pathlib.Path | None = None, buildDist: pathlib.Path | None = None):
    buildSrc = buildSrc if buildSrc else coxbuild.get_working_directory()
    buildDist = buildDist if buildDist else buildSrc.joinpath("dist")
    requirements = requirements if requirements else buildSrc.joinpath(
        "requirements.txt")

    mconfig["buildSrc"] = buildSrc.absolute()
    mconfig["buildDist"] = buildDist.absolute()
    mconfig["requirements"] = requirements.absolute()


settings()
