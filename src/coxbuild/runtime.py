from typing import TYPE_CHECKING

from coxbuild.configuration import Configuration, ConfigurationAccessor
from coxbuild.tasks import TaskContext

if TYPE_CHECKING:
    from coxbuild.managers import Manager
    from coxbuild.pipelines import Pipeline
    from coxbuild.services import EventContext, EventHandler, Service
    from coxbuild.tasks import Task


class ExecutionState(ConfigurationAccessor):
    __configname__ = "execution"

    @property
    def unmatchedTasks(self) -> list[str]:
        """Unmatched task names."""
        return self.config.get("unmatchedTasks") or []

    @unmatchedTasks.setter
    def unmatchedTasks(self, value: list[str]) -> None:
        self.config["unmatchedTasks"] = value

    @property
    def manager(self) -> "Manager | None":
        """Get manager."""
        return self.config.get("manager") or None

    @manager.setter
    def manager(self, value: "Manager | None") -> None:
        self.config["manager"] = value

    @property
    def pipeline(self) -> "Pipeline | None":
        """Get pipeline."""
        return self.config.get("pipeline") or None

    @pipeline.setter
    def pipeline(self, value: "Pipeline | None") -> None:
        self.config["pipeline"] = value

    @property
    def task(self) -> "Task | None":
        """Get task."""
        return self.config.get("task") or None

    @task.setter
    def task(self, value: "Task | None") -> None:
        self.config["task"] = value

    @property
    def service(self) -> "Service | None":
        """Get service."""
        return self.config.get("service") or None

    @service.setter
    def service(self, value: "Service | None") -> None:
        self.config["service"] = value

    @property
    def handler(self) -> "EventHandler | None":
        """Get event handler."""
        return self.config.get("handler") or None

    @handler.setter
    def handler(self, value: "EventHandler | None") -> None:
        self.config["handler"] = value

    @property
    def event(self) -> "EventContext | None":
        """Get event context."""
        return self.config.get("event") or None

    @event.setter
    def event(self, value: "EventContext | None") -> None:
        self.config["event"] = value

    @property
    def configuration(self) -> Configuration | None:
        """Get configuration."""
        return self.config.get("config") or None

    @configuration.setter
    def configuration(self, value: Configuration | None) -> None:
        self.config["config"] = value


def withExecutionState(task: "Task") -> "Task":
    """Decorator to add executionState argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(executionState=ExecutionState(context.config))

    task.before(hook)
    return task


def withManager(task: "Task") -> "Task":
    """Decorator to add manager argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(manager=ExecutionState(context.config).manager)

    task.before(hook)
    return task


def withPipeline(task: "Task") -> "Task":
    """Decorator to add pipeline argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(
                pipeline=ExecutionState(context.config).pipeline)

    task.before(hook)
    return task


def withService(task: "Task") -> "Task":
    """Decorator to add service argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(service=ExecutionState(context.config).service)

    task.before(hook)
    return task


def withTask(task: "Task") -> "Task":
    """Decorator to add task argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(task=ExecutionState(context.config).task)

    task.before(hook)
    return task


def withHandler(task: "Task") -> "Task":
    """Decorator to add handler argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(handler=ExecutionState(context.config).handler)

    task.before(hook)
    return task


def withEvent(task: "Task") -> "Task":
    """Decorator to add event argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(event=ExecutionState(context.config).event)

    task.before(hook)
    return task


def withConfiguration(task: "Task") -> "Task":
    """Decorator to add config argument to task context."""
    def hook(context: TaskContext):
        if context.config:
            context.kwds.update(config=ExecutionState(
                context.config).configuration)

    task.before(hook)
    return task
