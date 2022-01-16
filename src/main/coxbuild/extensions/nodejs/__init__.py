from pathlib import Path

import coxbuild
from coxbuild.schema import config, group, run

task = group("nodejs")


class Settings:
    mconfig = config.section("nodejs")

    @property
    @classmethod
    def src(cls) -> Path:
        return cls.mconfig["src"]

    @src.setter
    @classmethod
    def src(cls, value: Path) -> None:
        cls.mconfig["src"] = value


def settings(src: Path | None = None):
    src = src or coxbuild.get_working_directory()

    Settings.src = src.resolve()


settings()


@task()
def restore():
    """Restore npm packages (ci)."""
    run(["npm", "ci"], cwd=Settings.src, retry=3)


@task()
def build():
    """Build npm project."""
    run(["npm", "run", "build"], cwd=Settings.src)


@task()
def dev():
    """Run dev script."""
    run(["npm", "run", "dev"], cwd=Settings.src)


@task()
def serve():
    """Run serve script."""
    run(["npm", "run", "serve"], cwd=Settings.src)
