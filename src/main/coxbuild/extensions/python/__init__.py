from pathlib import Path

import coxbuild
from coxbuild.schema import config, group, run

task = group("python")


class Settings:
    mconfig = config.section("python")

    @property
    @classmethod
    def buildSrc(cls) -> Path:
        return cls.mconfig["buildSrc"]

    @buildSrc.setter
    @classmethod
    def buildSrc(cls, value: Path) -> None:
        cls.mconfig["buildSrc"] = value

    @property
    @classmethod
    def buildDist(cls) -> Path:
        return cls.mconfig["buildDist"]

    @buildDist.setter
    @classmethod
    def buildDist(cls, value: Path) -> None:
        cls.mconfig["buildDist"] = value

    @property
    @classmethod
    def requirements(cls) -> Path:
        return cls.mconfig["requirements"]

    @requirements.setter
    @classmethod
    def requirements(cls, value: Path) -> None:
        cls.mconfig["requirements"] = value


def settings(requirements: Path | None = None, buildSrc: Path | None = None, buildDist: Path | None = None):
    buildSrc = buildSrc or coxbuild.get_working_directory()
    buildDist = buildDist or buildSrc.joinpath("dist")
    requirements = requirements or buildSrc.joinpath(
        "requirements.txt")

    Settings.buildSrc = buildSrc.resolve()
    Settings.buildDist = buildDist.resolve()
    Settings.requirements = requirements.resolve()


settings()
