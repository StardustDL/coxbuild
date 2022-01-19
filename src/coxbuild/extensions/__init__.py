from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run


class ProjectSettings:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def test(self) -> Path:
        """Path to test code."""
        return self.config.get("test") or coxbuild.get_working_directory().joinpath("test").resolve()

    @test.setter
    def test(self, value: Path) -> None:
        self.config["test"] = value.resolve()

    @property
    def src(self) -> Path:
        """Source code path to build."""
        return self.config.get("src") or coxbuild.get_working_directory().joinpath("src").resolve()

    @src.setter
    def src(self, value: Path) -> None:
        self.config["src"] = value.resolve()

    @property
    def package(self) -> Path:
        """Distribution path for building."""
        return self.config.get("package") or coxbuild.get_working_directory().joinpath("dist").resolve()

    @package.setter
    def package(self, value: Path) -> None:
        self.config["package"] = value.resolve()

    @property
    def docs(self) -> Path:
        """Path to docs source."""
        return self.config.get("docs") or coxbuild.get_working_directory().joinpath("docs").resolve()

    @docs.setter
    def docs(self, value: Path) -> None:
        self.config["docs"] = value.resolve()


projectSettings = ProjectSettings(config.section("project"))
