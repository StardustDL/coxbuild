from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run

task = group("python")


class Settings:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def test(self) -> Path:
        """Path to test code."""
        return self.config.get("test") or coxbuild.get_working_directory().resolve()

    @test.setter
    def test(self, value: Path) -> None:
        self.config["test"] = value.resolve()

    @property
    def buildSrc(self) -> Path:
        """Source code path to build."""
        return self.config.get("buildSrc") or coxbuild.get_working_directory().resolve()

    @buildSrc.setter
    def buildSrc(self, value: Path) -> None:
        self.config["buildSrc"] = value.resolve()

    @property
    def buildDist(self) -> Path:
        """Distribution path for building."""
        return self.config.get("buildDist") or self.buildSrc.joinpath("dist").resolve()

    @buildDist.setter
    def buildDist(self, value: Path) -> None:
        print(self.buildDist)
        self.config["buildDist"] = value.resolve()

    @property
    def requirements(self) -> Path:
        """Path to requirements.txt."""
        return self.config.get("requirements") or self.buildSrc.joinpath("requirements.txt").resolve()

    @requirements.setter
    def requirements(self, value: Path) -> None:
        self.config["requirements"] = value.resolve()


settings = Settings(config.section("python"))
