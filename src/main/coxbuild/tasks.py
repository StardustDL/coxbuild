from dataclasses import dataclass
from datetime import datetime, timedelta
from timeit import default_timer as timer
from typing import Any, Callable
import traceback

from coxbuild.exceptions import CoxbuildException


def EMPTY_BODY() -> None:
    pass


@dataclass
class TaskResult:
    name: str
    duration: timedelta
    exception: CoxbuildException | None

    def __bool__(self):
        return self.exception is None


class Task:
    def __init__(self, name: str = "default", body: Callable[[], None] | None = None, deps: list[str] | None = None) -> None:
        self.name = name
        self.body = body if body else EMPTY_BODY
        self.deps = deps if deps else []
        self.result = None

    def __enter__(self) -> Callable[[], None]:
        print(f"{'-'*5} Task {self.name} (Start @ {datetime.now()}) {'-'*5}")

        self.result = None
        self._tic = timer()
        return self.body

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        duration = timedelta(seconds=timer()-self._tic)
        exception = None if exc_value is None else CoxbuildException(
            f"Failed to run task: {self.name}", cause=exc_value)
        self.result = TaskResult(
            self.name, duration=duration, exception=exception)

        print(f"{'-'*5} Task {self.name} ({'SUCCESS' if self.result else 'FAILED'} @ {self.result.duration}) {'-'*5}")

        del self._tic

        if exc_value is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb)

        return True
