import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from timeit import default_timer as timer
from typing import Any, Callable

from coxbuild.exceptions import CoxbuildException

logger = logging.getLogger("tasks")


def EMPTY_BODY() -> None:
    pass


@dataclass
class TaskResult:
    name: str
    duration: timedelta
    exception: CoxbuildException | None

    def __bool__(self):
        return self.exception is None

    @property
    def description(self) -> str:
        return "SUCCESS" if self else "FAILED"


class Task:
    def __init__(self, name: str = "default", body: Callable[[], None] | None = None, deps: list[str] | None = None) -> None:
        self.name = name
        self.body = body if body else EMPTY_BODY
        self.deps = deps if deps else []
        self.result = None

    def __enter__(self) -> Callable[[], None]:
        logger.debug(f"Start task {self.name}.")
        print(f"{'>'*3} Task {self.name} (Start @ {datetime.now()})")

        self.result = None
        self._tic = timer()
        return self.body

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        duration = timedelta(seconds=timer()-self._tic)
        exception = None if exc_value is None else CoxbuildException(
            f"Failed to run task: {self.name}", cause=exc_value)
        self.result = TaskResult(
            self.name, duration=duration, exception=exception)

        print(
            f"{'<'*3} Task {self.name} ({self.result.description} @ {self.result.duration})")

        if exc_value is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb)

        logger.debug(f"Finish task {self.name}: {self.result}.")

        del self._tic
        return True
