from pathlib import Path

import coxbuild
from coxbuild.configuration import Configuration, ConfigurationAccessor
from coxbuild.schema import group, run, task
from coxbuild.tasks import Task, TaskContext

from .. import ProjectSettings

grouped = group("python")


class Settings(ConfigurationAccessor):
    __configname__ = "python"

    def __init__(self, config: Configuration) -> None:
        super().__init__(config)
        self.project = ProjectSettings(config)

    @property
    def requirements(self) -> Path:
        """Path to requirements.txt."""
        return self.getPath("requirements") or self.project.src.joinpath("requirements.txt").resolve()

    @requirements.setter
    def requirements(self, value: Path) -> None:
        self.config["requirements"] = value.resolve()


def withSettings(task: Task) -> Task:
    """Decorator to add settings argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(settings=Settings(context.config))

    task.before(hook)
    return task
