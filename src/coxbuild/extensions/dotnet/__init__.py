from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group, run, task

from .. import projectSettings

grouped = group("dotnet")


class Settings:
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def version(self) -> str | None:
        """Build version."""
        return self.config.get("version") or None

    @version.setter
    def version(self, value: str | None) -> None:
        self.config["version"] = value

    @property
    def buildConfig(self) -> str:
        """Build configuration."""
        return self.config.get("buildConfig") or "Release"

    @buildConfig.setter
    def buildConfig(self, value: str) -> None:
        self.config["buildConfig"] = value

    @property
    def nugetSource(self) -> str:
        """Url to NuGet source."""
        return self.config.get("nugetSource") or "https://api.nuget.org/v3/index.json"

    @nugetSource.setter
    def nugetSource(self, value: str) -> None:
        self.config["nugetSource"] = value

    @property
    def nugetToken(self) -> str:
        """Token to NuGet source."""
        return self.config.get("nugetToken") or ""

    @nugetToken.setter
    def nugetToken(self, value: str) -> None:
        self.config["nugetToken"] = value


settings = Settings(config.section("dotnet"))


@grouped
@task
def restore():
    run(["dotnet", "restore"], cwd=projectSettings.src, retry=3)


@grouped
@task
def build():
    args = ["dotnet", "build", "-c", settings.buildConfig]
    if settings.version:
        args.append(f"/p:Version={settings.version}")
    run(args, cwd=projectSettings.src)


@grouped
@task
def pack():
    args = ["dotnet", "pack", "-c", settings.buildConfig]
    if settings.version:
        args.append(f"/p:Version={settings.version}")
    args.extend(["-o", str(projectSettings.package)])
    run(args, cwd=projectSettings.src)


@grouped
@task
def push():
    run(["dotnet", "nuget", "push", f"{str(projectSettings.package)}/*",
        "-s", settings.nugetSource, "-k", settings.nugetToken])
