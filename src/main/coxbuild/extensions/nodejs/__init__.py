from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run

task = group("nodejs")


class Settings:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def src(self) -> Path:
        """Path to source code."""
        return self.config.get("src") or coxbuild.get_working_directory().resolve()

    @src.setter
    def src(self, value: Path) -> None:
        self.config["src"] = value.resolve()


settings = Settings(config.section("nodejs"))


@task()
def restore():
    """Restore npm packages (ci)."""
    run(["npm", "ci"], cwd=settings.src, retry=3)


@task()
def build():
    """Build npm project."""
    run(["npm", "run", "build"], cwd=settings.src)


@task()
def dev():
    """Run dev script."""
    run(["npm", "run", "dev"], cwd=settings.src)


@task()
def serve():
    """Run serve script."""
    run(["npm", "run", "serve"], cwd=settings.src)
