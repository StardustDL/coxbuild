import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from graphlib import TopologicalSorter
from queue import Queue
from timeit import default_timer as timer
from typing import Any, Callable, Tuple

from coxbuild.exceptions import CoxbuildException
from coxbuild.runners import Runner
from coxbuild.tasks import Task, TaskResult

logger = logging.getLogger("manager")


@dataclass
class ManagedRunnerResult:
    duration: timedelta
    tasks: list[TaskResult]
    exception: CoxbuildException | None = None

    def __bool__(self):
        return self.exception is None and all(self.tasks)

    @property
    def description(self) -> str:
        return "🟢 SUCCESS" if self else "🔴 FAILING"


class ManagedRunner(Runner):
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks
        self.result = None

        super().__init__(self._run)

    def _run(self):
        n = len(self.tasks)
        for i, task in enumerate(self.tasks):
            logger.debug(f"Run task {i+1}({task.name}) of {n} tasks")
            print(f"{'-'*15} ({i+1}/{n}) 📜 Task {task.name} {'-'*15}")

            res = task.invoke()

            print("")
            self._results.append(res)
            if not res:
                break

    def __enter__(self) -> Callable[[], None]:
        logger.debug("Running")
        print(f"{'-'*20} ⌛ Running 🕰️ {datetime.now()} {'-'*20}\n")

        self.result = None
        self._results: list[TaskResult] = []

        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        super().__exit__(exc_type, exc_value, exc_tb)

        exception = None if self.exc_value is None else CoxbuildException(
            f"Failed to run runner", cause=self.exc_value)
        self.result = ManagedRunnerResult(
            duration=self.duration, tasks=self._results, exception=exception)

        print(
            f"{'-'*20} 📋 Done {self.result.description} (⏱️ {self.result.duration}) {'-'*20}")

        if self.result.exception:
            print(f"⚠️ Exception: {self.result.exception}")
        for tr in self.result.tasks:
            print(f"{tr.description} ⏱️ {tr.duration} 📜 {tr.name}")

        if self.exc_value is not None:
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_tb)

        logger.info(f"Finish: {self.result}")

        del self._results

        return True


class Manager:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        if task.name in self.tasks:
            raise CoxbuildException(
                f"Register multiple task with the same name {task.name}.")
        self.tasks[task.name] = task
        logger.debug(f"Register task {task.name}")

    def __call__(self, *args: Any, **kwds: Any) -> ManagedRunner:
        tks = set()
        q: Queue[str] = Queue()
        for name in args:
            if name in self.tasks and name not in tks:
                tks.add(name)
                q.put(name)
        while not q.empty():
            t = q.get()
            for d in self.tasks[t].deps:
                if d in self.tasks and d not in tks:
                    tks.add(d)
                    q.put(d)

        graph = {}

        for key in tks:
            graph[key] = {d for d in self.tasks[key].deps}

        tasks = list((self.tasks[name]
                     for name in TopologicalSorter(graph).static_order()))

        logger.debug(f"Tasks to run: {', '.join((t.name for t in tasks))}")

        return ManagedRunner(tasks)

    def invoke(self, *args: Any, **kwds: Any) -> ManagedRunnerResult:
        runner = self(*args, **kwds)
        with runner as run:
            run()
        return runner.result
