from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run, task

from .. import projectSettings

grouped = group("python")


class Settings:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def requirements(self) -> Path:
        """Path to requirements.txt."""
        return self.config.get("requirements") or projectSettings.src.joinpath("requirements.txt").resolve()

    @requirements.setter
    def requirements(self, value: Path) -> None:
        self.config["requirements"] = value.resolve()


settings = Settings(config.section("python"))
