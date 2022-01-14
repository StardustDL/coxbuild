import logging
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from graphlib import TopologicalSorter
from queue import Queue
from timeit import default_timer as timer
from typing import Any, Callable, Tuple

from coxbuild.exceptions import CoxbuildException
from coxbuild.runners import Runner
from coxbuild.tasks import Task, TaskResult

logger = logging.getLogger("manager")


@dataclass
class TaskContext:
    task: Task
    args: list[Any] = field(default_factory=list)
    kwds: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskHook:
    before: Callable[[TaskContext], bool] | None = None
    setup: Callable[..., None] | None = None
    teardown: Callable[..., None] | None = None
    after: Callable[[TaskContext, TaskResult], None] | None = None


@dataclass
class PipelineContext:
    tasks: list[TaskResult]


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


@dataclass
class PipelineHook:
    setup: Callable[[PipelineContext], bool] | None = None
    before: Callable[[TaskContext], bool] | None = None
    after: Callable[[TaskContext, TaskResult], None] | None = None
    teardown: Callable[[PipelineContext, PipelineResult], None] | None = None


class PipelineRunner(Runner):
    def __init__(self, tasks: list[Task], hooks: dict[str, TaskHook], phook: PipelineHook) -> None:
        self.tasks = tasks
        self.hooks = hooks
        self.phook = phook
        self.context = PipelineContext(self.tasks)
        self.result = None

        super().__init__(self._run)

    def _run(self):
        n = len(self.tasks)

        if self.phook.setup:
            logger.debug(f"Run pipeline setup hook")
            if self.phook.setup(self.context) == False:
                message = "Stop pipeline running by pipeline setup hook"
                logger.info(message)
                print(message)
                return

        print("")

        for i, task in enumerate(self.tasks):
            logger.debug(f"Run task {i+1}({task.name}) of {n} tasks")
            print(f"{'-'*15} ({i+1}/{n}) 📜 Task {task.name} {'-'*15}")
            print("")

            hook = self.hooks.get(task.name)

            tcontext = TaskContext(task)

            if self.phook.before:
                logger.debug(f"Run pipeline before hook for {task.name}")
                if self.phook.before(tcontext) == False:
                    message = f"Stop task {task.name} running by pipeline before hook"
                    logger.info(message)
                    print(message)
                    continue

            if hook and hook.before:
                logger.debug(f"Run task before hook for {task.name}")
                if hook.before(tcontext) == False:
                    message = f"Stop task {task.name} running by task before hook"
                    logger.info(message)
                    print(message)
                    continue

            setup = hook.setup if hook and hook.setup else None
            teardown = hook.teardown if hook and hook.teardown else None

            res = task.invoke(*tcontext.args, **tcontext.kwds,
                              setup=setup, teardown=teardown)

            self._results.append(res)

            if hook and hook.after:
                logger.debug(f"Run task after hook for {task.name}")
                hook.after(tcontext, res)

            if self.phook.after:
                logger.debug(f"Run pipeline after hook for {task.name}")
                self.phook.after(tcontext, res)

            print("")

            if not res:
                break

    def __enter__(self) -> Callable[[], None]:
        logger.debug("Running")
        print(f"{'-'*20} ⌛ Running 🕰️ {datetime.now()} {'-'*20}")

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

        if self.phook.teardown is not None:
            self.phook.teardown(self.context, self.result)

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
        self.phook: PipelineHook = PipelineHook()

    def register(self, task: Task) -> None:
        if task.name in self.tasks:
            raise CoxbuildException(
                f"Register multiple task with the same name {task.name}.")
        self.tasks[task.name] = task
        logger.debug(f"Register task {task.name}")

    def hook(self, thook: TaskHook | PipelineHook, name: str | None = None) -> None:
        if isinstance(thook, TaskHook):
            if name:
                self.hooks[name] = thook
            else:
                raise CoxbuildException("Empty task name for task hook.")
        elif isinstance(thook, PipelineHook):
            if name:
                raise CoxbuildException(
                    "Nonempty pipeline name for pipeline hook.")
            else:
                self.phook = thook

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

        return PipelineRunner(tasks, {k: v for k, v in self.hooks.items() if k in tks}, self.phook)

    def invoke(self, *args: str, **kwds: Any) -> PipelineResult:
        runner = self(*args, **kwds)
        with runner as run:
            run()
        return runner.result
