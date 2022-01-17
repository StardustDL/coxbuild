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
    def src(self) -> Path:
        """Source code path to build."""
        return self.config.get("src") or coxbuild.get_working_directory().resolve()

    @src.setter
    def src(self, value: Path) -> None:
        self.config["src"] = value.resolve()

    @property
    def package(self) -> Path:
        """Distribution path for building."""
        return self.config.get("package") or self.src.joinpath("dist").resolve()

    @package.setter
    def package(self, value: Path) -> None:
        self.config["package"] = value.resolve()

    @property
    def requirements(self) -> Path:
        """Path to requirements.txt."""
        return self.config.get("requirements") or self.src.joinpath("requirements.txt").resolve()

    @requirements.setter
    def requirements(self, value: Path) -> None:
        self.config["requirements"] = value.resolve()
    
    @property
    def apidocs(self) -> Path:
        """Path to apidocs source."""
        return self.config.get("apidocs") or coxbuild.get_working_directory().resolve()

    @apidocs.setter
    def apidocs(self, value: Path) -> None:
        self.config["apidocs"] = value.resolve()


settings = Settings(config.section("python"))
