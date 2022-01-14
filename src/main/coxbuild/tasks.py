import logging
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from timeit import default_timer as timer
from typing import Any, Callable

from coxbuild.exceptions import CoxbuildException
from coxbuild.runners import Runner

logger = logging.getLogger("tasks")


@dataclass
class TaskResult:
    name: str
    duration: timedelta
    exception: CoxbuildException | None

    def __bool__(self):
        return self.exception is None

    @property
    def description(self) -> str:
        return "🟢 SUCCESS" if self else "🔴 FAILING"

    def ensure(self) -> None:
        if not self:
            raise self.exception


class Task:
    def __init__(self, name: str = "default",
                 body: Callable[..., None] | None = None,
                 deps: list[str] | None = None,
                 precondition: Callable[..., bool] | None = None,
                 postcondition: Callable[..., bool] | None = None
                 ) -> None:
        self.name = name
        self.body = body
        self.deps = deps if deps else []
        self.precondition = precondition
        self.postcondition = postcondition

    def __call__(self, *args: Any, setup: Callable[..., None] | None = None, teardown: Callable[..., None] | None = None, **kwds: Any):
        return TaskRunner(self, args, kwds, setup, teardown)

    def invoke(self, *args: Any, setup: Callable[..., None] | None = None, teardown: Callable[..., None] | None = None, **kwds: Any) -> TaskResult:
        runner = self(*args, setup=setup, teardown=teardown, **kwds)
        with runner as run:
            run()
        return runner.result


class TaskRunner(Runner):
    def __init__(self, task: Task, args: list[Any], kwds: dict[str, Any],  setup: Callable[..., None] | None = None, teardown: Callable[..., None] | None = None) -> None:
        self.task = task
        self.args = args
        self.kwds = kwds
        self.setup = setup
        self.teardown = teardown

        super().__init__(self._run)

    def _run(self):
        if self.task.precondition is not None:
            pre = self.task.precondition(*self.args, **self.kwds)
            if not pre:
                message = f"Task {self.task.name} ignored: precondition filtered"
                logger.info(message)
                print(message)
                return

        if self.setup is not None:
            self.setup(*self.args, **self.kwds)

        if self.task.body is not None:
            self.task.body(*self.args, **self.kwds)

        if self.teardown is not None:
            self.teardown(*self.args, **self.kwds)

        if self.task.postcondition is not None:
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
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_tb, file=sys.stdout)

        logger.debug(f"Finish task {self.task.name}: {self.result}.")

        print(
            f"{'-'*3} 🔺 {self.task.name} {self.result.description} ⏱️ {self.result.duration} {'-'*3}")

        return True
