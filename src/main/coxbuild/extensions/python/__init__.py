from pathlib import Path

import coxbuild
from coxbuild.schema import config, group, run

task = group("python")


class Settings:
    mconfig = config.section("python")

    @classmethod
    @property
    def buildSrc(cls) -> Path:
        return cls.mconfig["buildSrc"]

    @classmethod
    @buildSrc.setter
    def buildSrc(cls, value: Path) -> None:
        cls.mconfig["buildSrc"] = value

    @classmethod
    @property
    def buildDist(cls) -> Path:
        return cls.mconfig["buildDist"]

    @classmethod
    @buildDist.setter
    def buildDist(cls, value: Path) -> None:
        cls.mconfig["buildDist"] = value

    @classmethod
    @property
    def requirements(cls) -> Path:
        return cls.mconfig["requirements"]

    @classmethod
    @requirements.setter
    def requirements(cls, value: Path) -> None:
        cls.mconfig["requirements"] = value


def settings(requirements: Path | None = None, buildSrc: Path | None = None, buildDist: Path | None = None):
    buildSrc = buildSrc if buildSrc else coxbuild.get_working_directory()
    buildDist = buildDist if buildDist else buildSrc.joinpath("dist")
    requirements = requirements if requirements else buildSrc.joinpath(
        "requirements.txt")

    Settings.buildSrc = buildSrc.absolute()
    Settings.buildDist = buildDist.absolute()
    Settings.requirements = requirements.absolute()


settings()
