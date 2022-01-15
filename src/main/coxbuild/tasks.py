import logging
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

from .exceptions import CoxbuildException
from .runners import Runner

logger = logging.getLogger("tasks")


@dataclass
class TaskResult:
    """Execution result for task."""
    name: str
    """task name"""
    duration: timedelta
    """execution duration"""
    exception: CoxbuildException | None
    """exception when running"""

    def __bool__(self):
        return self.exception is None

    @property
    def description(self) -> str:
        """Return result's description string."""
        return "🟢 SUCCESS" if self else "🔴 FAILING"

    def ensure(self) -> None:
        """Ensure the result is success, otherwise re-raise exception."""
        if not self:
            raise self.exception


class Task:
    """Task."""

    def __init__(self, name: str = "default",
                 body: Callable[..., None] | None = None,
                 doc: str = "",
                 deps: list[str] | None = None,
                 precondition: Callable[..., bool] | None = None,
                 postcondition: Callable[..., bool] | None = None
                 ) -> None:
        """
        Create task.

        name: task name
        body: task body
        doc: task document
        deps: dependency task names
        precondition: condition to decide whether to run the task
        postcondition: condition to decide whether the task succeed
        """
        self.name = name
        self.body = body
        self.doc = doc
        self.deps = deps or []
        self.precondition = precondition
        self.postcondition = postcondition

    def __call__(self, *args: Any, setup: Callable[..., None] | None = None, teardown: Callable[..., None] | None = None, **kwds: Any):
        runner = self.build(*args, setup=setup, teardown=teardown, **kwds)
        with runner as run:
            run()
        return runner.result

    def build(self, *args: Any, setup: Callable[..., None] | None = None, teardown: Callable[..., None] | None = None, **kwds: Any):
        """
        Build runner of task.

        args: task arguments
        kwds: task keyword arguments
        setup: setup hook
        teardown: teardown hook
        """
        return TaskRunner(self, args, kwds, setup, teardown)


class TaskRunner(Runner):
    """Runner for task."""

    def __init__(self, task: Task, args: list[Any], kwds: dict[str, Any],  setup: Callable[..., None] | None = None, teardown: Callable[..., None] | None = None) -> None:
        self.task = task
        """task to run"""
        self.args = args
        """task arguments"""
        self.kwds = kwds
        """task keyword arguments"""
        self.setup = setup
        """setup hook"""
        self.teardown = teardown
        """teardown hook"""

        super().__init__(self._run)

    def _run(self):
        if self.task.precondition is not None:
            logger.debug(f"Task {self.task.name} check precondition.")
            pre = self.task.precondition(*self.args, **self.kwds)
            if not pre:
                message = f"Task {self.task.name} ignored: precondition filtered"
                logger.info(message)
                print(message)
                return

        if self.setup is not None:
            logger.debug(f"Task {self.task.name} setup hook.")
            self.setup(*self.args, **self.kwds)

        try:
            if self.task.body is not None:
                logger.debug(f"Task {self.task.name} body execute.")
                self.task.body(*self.args, **self.kwds)
        finally:
            if self.teardown is not None:
                logger.debug(f"Task {self.task.name} teardown hook.")
                self.teardown(*self.args, **self.kwds)

        if self.task.postcondition is not None:
            logger.debug(f"Task {self.task.name} check postcondition.")
            post = self.task.postcondition(*self.args, **self.kwds)
            if not post:
                raise CoxbuildException(
                    f"Task {self.task.name} failed: postcondition checking broken")

    def __enter__(self) -> Callable[[], None]:
        logger.debug(f"Start task {self.task.name}.")
        print(f"{'-'*3} 🔻 {self.task.name} 🕰️ {datetime.now()} {'-'*3}")

        self.result = None

        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        super().__exit__(exc_type, exc_value, exc_tb)

        exception = None if self.exc_value is None else CoxbuildException(
            f"Failed to run task: {self.task.name}", cause=self.exc_value)
        self.result = TaskResult(
            self.task.name, duration=self.duration, exception=exception)

        if self.exc_value is not None:
            logger.error("Task execute exception.", exc_info=self.exc_value)
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_tb, file=sys.stdout)

        logger.debug(f"Finish task {self.task.name}: {self.result}.")

        print(
            f"{'-'*3} 🔺 {self.task.name} {self.result.description} ⏱️ {self.result.duration} {'-'*3}")

        return True
