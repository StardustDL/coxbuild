import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable

import coxbuild
from coxbuild.configuration import Configuration, ConfigurationAccessor
from coxbuild.pipelines import PipelineHook
from coxbuild.services import EventHandler
from coxbuild.tasks import Task, TaskContext


@dataclass
class Extension:
    uri: str = ""
    name: str = ""
    description: str = ""
    version: str = ""
    hashcode: str = ""
    module: ModuleType | None = None

    @property
    def tasks(self) -> Iterable[Task]:
        if not self.module:
            return
        for name, member in inspect.getmembers(self.module):
            if name.startswith("_"):
                continue

            match member:
                case Task() as t:
                    yield t

    @property
    def events(self) -> Iterable[EventHandler]:
        if not self.module:
            return
        for name, member in inspect.getmembers(self.module):
            if name.startswith("_"):
                continue

            match member:
                case EventHandler() as t:
                    yield t

    @property
    def pipelineHooks(self) -> Iterable[PipelineHook]:
        if not self.module:
            return
        for name, member in inspect.getmembers(self.module):
            if name.startswith("_"):
                continue

            match member:
                case PipelineHook() as t:
                    yield t


class ProjectSettings(ConfigurationAccessor):
    __configname__ = "project"

    @property
    def test(self) -> Path:
        """Path to test code."""
        return self.getPath("test") or coxbuild.get_working_directory().joinpath("test").resolve()

    @test.setter
    def test(self, value: Path) -> None:
        self.config["test"] = value.resolve()

    @property
    def src(self) -> Path:
        """Source code path to build."""
        return self.getPath("src") or coxbuild.get_working_directory().joinpath("src").resolve()

    @src.setter
    def src(self, value: Path) -> None:
        self.config["src"] = value.resolve()

    @property
    def package(self) -> Path:
        """Distribution path for building."""
        return self.getPath("package") or coxbuild.get_working_directory().joinpath("dist").resolve()

    @package.setter
    def package(self, value: Path) -> None:
        self.config["package"] = value.resolve()

    @property
    def docs(self) -> Path:
        """Path to docs source."""
        return self.getPath("docs") or coxbuild.get_working_directory().joinpath("docs").resolve()

    @docs.setter
    def docs(self, value: Path) -> None:
        self.config["docs"] = value.resolve()


def withProject(task: Task) -> Task:
    """Decorator to add project argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(project=ProjectSettings(context.config))

    task.before(hook)
    return task
