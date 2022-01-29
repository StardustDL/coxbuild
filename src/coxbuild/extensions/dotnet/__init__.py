from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration, ConfigurationAccessor
from coxbuild.schema import group, run, task
from coxbuild.tasks import Task, TaskContext

from .. import ProjectSettings, withProject

grouped = group("dotnet")


class Settings(ConfigurationAccessor):
    def __init__(self, config: Configuration) -> None:
        self.config = config

    @property
    def version(self) -> str | None:
        """Build version."""
        return self.get("version") or None

    @version.setter
    def version(self, value: str | None) -> None:
        self.config["version"] = value

    @property
    def buildConfig(self) -> str:
        """Build configuration."""
        return self.get("buildConfig") or "Release"

    @buildConfig.setter
    def buildConfig(self, value: str) -> None:
        self.config["buildConfig"] = value

    @property
    def nugetSource(self) -> str:
        """Url to NuGet source."""
        return self.get("nugetSource") or "https://api.nuget.org/v3/index.json"

    @nugetSource.setter
    def nugetSource(self, value: str) -> None:
        self.config["nugetSource"] = value

    @property
    def nugetToken(self) -> str:
        """Token to NuGet source."""
        return self.get("nugetToken") or ""

    @nugetToken.setter
    def nugetToken(self, value: str) -> None:
        self.config["nugetToken"] = value


def withSettings(task: Task) -> Task:
    """Decorator to add settings argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(settings=Settings(context.config))

    task.before(hook)
    return task


@grouped
@withProject
@task
def restore(*, project: ProjectSettings):
    run(["dotnet", "restore"], cwd=project.src, retry=3)


@grouped
@withProject
@withSettings
@task
def build(*, project: ProjectSettings, settings: Settings):
    args = ["dotnet", "build", "-c", settings.buildConfig]
    if settings.version:
        args.append(f"/p:Version={settings.version}")
    run(args, cwd=project.src)


@grouped
@withProject
@withSettings
@task
def pack(*, project: ProjectSettings, settings: Settings):
    args = ["dotnet", "pack", "-c", settings.buildConfig]
    if settings.version:
        args.append(f"/p:Version={settings.version}")
    args.extend(["-o", str(project.package)])
    run(args, cwd=project.src)


@grouped
@withProject
@withSettings
@task
def push(*, project: ProjectSettings, settings: Settings):
    run(["dotnet", "nuget", "push", f"{str(project.package)}/*",
        "-s", settings.nugetSource, "-k", settings.nugetToken])
