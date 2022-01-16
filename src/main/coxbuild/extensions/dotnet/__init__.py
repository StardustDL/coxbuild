from pathlib import Path

import coxbuild
from coxbuild.schema import config, group, run

task = group("dotnet")


class Settings:
    mconfig = config.section("dotnet")

    @property
    @classmethod
    def src(cls) -> Path:
        return cls.mconfig["src"]

    @src.setter
    @classmethod
    def src(cls, value: Path) -> None:
        cls.mconfig["src"] = value

    @property
    @classmethod
    def buildVersion(cls) -> Path:
        return cls.mconfig["buildVersion"]

    @buildVersion.setter
    @classmethod
    def buildVersion(cls, value: Path) -> None:
        cls.mconfig["buildVersion"] = value

    @property
    @classmethod
    def buildConfig(cls) -> Path:
        return cls.mconfig["buildConfig"]

    @buildConfig.setter
    @classmethod
    def buildConfig(cls, value: Path) -> None:
        cls.mconfig["buildConfig"] = value


def settings(src: Path | None = None):
    src = src or coxbuild.get_working_directory()

    Settings.src = src.resolve()


settings()


@task()
def restore():
    run(["dotnet", "restore"], cwd=Settings.src, retry=3)


@task()
def build():
    run(["dotnet", "build", "-c", "Release",
        "/p:Version=$build_version"], cwd=Settings.src)


@task()
def pack():
    run(["dotnet", "pack", "-c", "Release",
        "/p:Version=$build_version", "-o", "dist"], cwd=Settings.src)


@task()
def push():
    run(["dotnet", "nuget", "push", "dist/*.nupkg", "-s",
        "https://api.nuget.org/v3/index.json", "-k", "token"])
