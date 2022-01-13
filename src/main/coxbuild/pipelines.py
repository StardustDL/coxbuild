from enum import Enum
import logging
import sys
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
class TaskHook:
    before: Callable[..., None] | None = None
    after: Callable[..., None] | None = None
    args: Callable[[], list[Any]] | None = None
    kwds: Callable[[], dict[str, Any]] | None = None


@dataclass
class PipelineResult:
    duration: timedelta
    tasks: list[TaskResult]
    exception: CoxbuildException | None = None

    def __bool__(self):
        return self.exception is None and all(self.tasks)

    @property
    def description(self) -> str:
        return "🟢 SUCCESS" if self else "🔴 FAILING"


class PipelineRunner(Runner):
    def __init__(self, tasks: list[Task], hooks: dict[str, TaskHook]) -> None:
        self.tasks = tasks
        self.hooks = hooks
        self.result = None

        super().__init__(self._run)

    def _run(self):
        n = len(self.tasks)
        for i, task in enumerate(self.tasks):
            logger.debug(f"Run task {i+1}({task.name}) of {n} tasks")
            print(f"{'-'*15} ({i+1}/{n}) 📜 Task {task.name} {'-'*15}")

            hook = self.hooks.get(task.name)

            args = []
            kwds = {}

            if hook is not None:
                if hook.args is not None:
                    logger.debug(f"Run args hook for {task.name}")
                    args = hook.args()
                if hook.kwds is not None:
                    logger.debug(f"Run kwds hook for {task.name}")
                    kwds = hook.kwds()
            if hook is not None and hook.before is not None:
                logger.debug(f"Run before hook for {task.name}")
                hook.before(*args, **kwds)

            res = task.invoke(*args, **kwds)

            if hook is not None and hook.after is not None:
                logger.debug(f"Run after hook for {task.name}")
                hook.after(*args, **kwds)

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
        self.result = PipelineResult(
            duration=self.duration, tasks=self._results, exception=exception)

        if self.exc_value is not None:
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_tb, file=sys.stdout)

        logger.info(f"Finish: {self.result}")

        print(
            f"{'-'*20} 📋 Done {self.result.description} (⏱️ {self.result.duration}) {'-'*20}")

        cnt = len(self.result.tasks)

        for i, tr in enumerate(self.result.tasks):
            print(f"({i+1}/{cnt})\t{tr.description}\t⏱️ {tr.duration}\t📜 {tr.name}")

        del self._results

        return True


class Pipeline:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.hooks: dict[str, TaskHook] = {}

    def register(self, task: Task) -> None:
        if task.name in self.tasks:
            raise CoxbuildException(
                f"Register multiple task with the same name {task.name}.")
        self.tasks[task.name] = task
        logger.debug(f"Register task {task.name}")

    def hook(self, name: str, thook: TaskHook) -> None:
        self.hooks[name] = thook

    def __call__(self, *args: str, **kwds: Any) -> PipelineRunner:
        tks: set[str] = set()
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

        return PipelineRunner(tasks, {k: v for k, v in self.hooks.items() if k in tks})

    def invoke(self, *args: str, **kwds: Any) -> PipelineResult:
        runner = self(*args, **kwds)
        with runner as run:
            run()
        return runner.result
