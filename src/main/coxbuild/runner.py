import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from graphlib import TopologicalSorter
from queue import Queue
from timeit import default_timer as timer
from typing import Any, Callable, Tuple

from coxbuild.exceptions import CoxbuildException
from coxbuild.tasks import Task, TaskResult

logger = logging.getLogger("runner")


@dataclass
class RunnerResult:
    duration: timedelta
    tasks: list[TaskResult]
    exception: CoxbuildException | None = None

    def __bool__(self):
        return self.exception is None and all(self.tasks)

    @property
    def description(self) -> str:
        return "SUCCESS" if self else "FAILED"


class Runner:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks
        self.result = None

    def __enter__(self) -> Callable[[], None]:
        logger.debug("Running")
        print(f"{'-'*5} Running @ {datetime.now()} {'-'*5}")

        self.result = None
        self._tic = timer()
        self._results: list[TaskResult] = []

        def runner():
            n = len(self.tasks)
            for i, task in enumerate(self.tasks):
                logger.debug(f"Run task {i+1}({task.name}) of {n} tasks")
                print(f"{'-'*5} ({i+1}/{n}) Task {task.name} {'-'*5}")

                with task as run:
                    run()
                self._results.append(task.result)
                if not task.result:
                    break

        return runner

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        exception = None if exc_value is None else CoxbuildException(
            f"Failed to run runner", cause=exc_value)
        duration = timedelta(seconds=timer()-self._tic)
        self.result = RunnerResult(
            duration=duration, tasks=self._results, exception=exception)

        print(
            f"{'-'*5} Done ({self.result.description} @ {self.result.duration}) {'-'*5}")

        print(f"{self.result.description} @ {self.result.duration}")
        if self.result.exception:
            print(f"Exception: {self.result.exception}")
        for tr in self.result.tasks:
            print(f"  {tr.name}: {tr.description} @ {tr.duration}")

        if exc_value is not None:
            traceback.print_exception(exc_type, exc_value, exc_tb)

        logger.info(f"Finish: {self.result}")

        del self._tic
        del self._results

        return True
