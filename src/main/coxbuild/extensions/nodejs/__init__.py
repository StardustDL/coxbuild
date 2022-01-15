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
    src = src if src else coxbuild.get_working_directory()

    Settings.src = src.absolute()


settings()


@task()
def restore():
    run(["npm", "ci"], cwd=Settings.src, retry=3)


@task()
def build():
    run(["npm", "run", "build"], cwd=Settings.src)


@task()
def dev():
    run(["npm", "run", "dev"], cwd=Settings.src)


@task()
def serve():
    run(["npm", "run", "serve"], cwd=Settings.src)
