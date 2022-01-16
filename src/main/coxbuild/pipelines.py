import inspect
import logging
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from graphlib import TopologicalSorter
from queue import Queue
from typing import Any, Awaitable, Callable

from .exceptions import CoxbuildException
from .runners import Runner
from .tasks import Task, TaskResult

logger = logging.getLogger("manager")


@dataclass
class TaskContext:
    """Execution context for task."""
    task: Task
    """running task"""
    args: list[Any] = field(default_factory=list)
    """arguments"""
    kwds: dict[str, Any] = field(default_factory=dict)
    """keyword arguments"""


@dataclass
class TaskHook:
    """Hooks for a task."""
    before: Callable[[TaskContext], Awaitable[bool] | bool] | None = None
    """before task starting"""
    setup: Callable[..., Awaitable | None] | None = None
    """setup before task running"""
    teardown: Callable[..., Awaitable | None] | None = None
    """teardown after task running"""
    after: Callable[[TaskContext, TaskResult], Awaitable | None] | None = None
    """after task finished"""


@dataclass
class PipelineContext:
    """Execution context for pipeline."""
    tasks: list[TaskResult]
    """tasks in the pipeline"""


@dataclass
class PipelineResult:
    """Execution result for pipeline."""
    duration: timedelta
    """execution duration"""
    tasks: list[TaskResult]
    """tasks in the pipeline"""
    exception: CoxbuildException | None = None
    """exception when running"""

    def __bool__(self):
        return self.exception is None and all(self.tasks)

    @property
    def description(self) -> str:
        """Return result's description string."""
        return "🟢 SUCCESS" if self else "🔴 FAILING"


@dataclass
class PipelineHook:
    """Hooks for a pipeline."""
    setup: Callable[[PipelineContext], Awaitable[bool] | bool] | None = None
    """setup before pipeline running"""
    before: Callable[[TaskContext], Awaitable[bool] | bool] | None = None
    """before task starting"""
    after: Callable[[TaskContext, TaskResult], Awaitable | None] | None = None
    """after task finished"""
    teardown: Callable[[PipelineContext, PipelineResult],
                       Awaitable | None] | None = None
    """teardown after pipeline running"""


class PipelineRunner(Runner):
    """Runner for pipeline."""

    def __init__(self, tasks: list[Task], hooks: dict[str, TaskHook], phook: PipelineHook) -> None:
        """
        Create runner.

        tasks: tasks in the pipeline
        hooks: hooks for tasks
        phook: hook for pipeline
        """
        self.tasks = tasks
        self.hooks = hooks
        self.phook = phook
        self.context = PipelineContext(self.tasks)
        self.result = None

        super().__init__(self._run)

    async def _run(self):
        n = len(self.tasks)

        if self.phook.setup:
            logger.debug(f"Run pipeline setup hook")
            pre = self.phook.setup(self.context)
            if inspect.isawaitable(pre):
                pre: bool = await pre
            if pre == False:
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
                pre = self.phook.before(tcontext)
                if inspect.isawaitable(pre):
                    pre: bool = await pre
                if pre == False:
                    message = f"Stop task {task.name} running by pipeline before hook"
                    logger.info(message)
                    print(message)
                    continue

            if hook and hook.before:
                logger.debug(f"Run task before hook for {task.name}")
                pre = hook.before(tcontext)
                if inspect.isawaitable(pre):
                    pre: bool = await pre
                if pre == False:
                    message = f"Stop task {task.name} running by task before hook"
                    logger.info(message)
                    print(message)
                    continue

            setup = hook.setup if hook and hook.setup else None
            teardown = hook.teardown if hook and hook.teardown else None

            res = await task(*tcontext.args, **tcontext.kwds,
                             setup=setup, teardown=teardown)

            self._results.append(res)

            if hook and hook.after:
                logger.debug(f"Run task after hook for {task.name}")
                post = hook.after(tcontext, res)
                if inspect.isawaitable(post):
                    await post

            if self.phook.after:
                logger.debug(f"Run pipeline after hook for {task.name}")
                post = self.phook.after(tcontext, res)
                if inspect.isawaitable(post):
                    await post

            print("")

            if not res:
                break

    async def __aenter__(self) -> Callable[[], Awaitable | None]:
        logger.debug(f"Running pipeline: {self.tasks}")
        print(f"{'-'*20} ⌛ Running 🕰️ {datetime.now()} {'-'*20}")

        self.result = None
        self._results: list[TaskResult] = []

        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> bool:
        await super().__aexit__(exc_type, exc_value, exc_tb)

        exception = None if self.exc_value is None else CoxbuildException(
            f"Failed to run runner", cause=self.exc_value)
        self.result = PipelineResult(
            duration=self.duration, tasks=self._results, exception=exception)

        if self.exc_value is not None:
            logger.error("Task execute exception.", exc_info=self.exc_value)
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_tb, file=sys.stdout)

        if self.phook.teardown is not None:
            logger.debug(f"Pipeline teardown hook.")
            self.phook.teardown(self.context, self.result)

        logger.info(f"Finish pipeline: {self.result}")

        print(
            f"{'-'*20} 📋 Done {self.result.description} (⏱️ {self.result.duration}) {'-'*20}")

        cnt = len(self.result.tasks)

        for i, tr in enumerate(self.result.tasks):
            print(f"({i+1}/{cnt})\t{tr.description}\t⏱️ {tr.duration}\t📜 {tr.name}")

        del self._results

        return True

    def __await__(self):
        yield from super().__await__()
        return self.result


class Pipeline:
    """Pipeline to run tasks."""

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        """tasks in the pipeline"""
        self.hooks: dict[str, TaskHook] = {}
        """hooks for tasks"""
        self.phook: PipelineHook = PipelineHook()
        """hook for pipeline"""

    def register(self, task: Task) -> None:
        """
        Register a task into pipeline.

        task: task to register
        """
        if task.name in self.tasks:
            raise CoxbuildException(
                f"Register multiple task with the same name {task.name}.")
        self.tasks[task.name] = task
        logger.debug(f"Register task {task.name}")

    def hook(self, thook: TaskHook | PipelineHook, name: str | None = None) -> None:
        """
        Hook task or pipeline.

        thook: the updated hook
        name: the hooked task's name, None for pipeline hook
        """

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

    def __call__(self, *args: str | Task, **kwds: Any):
        """
        Build runner of pipeline.

        args: list of tasks or task names
        """

        logger.debug(f"Build pipeline by {args}.")

        tks: set[str] = set()
        q: Queue[str] = Queue()
        for name in args:
            if isinstance(name, Task):
                name = name.name
            if name in self.tasks and name not in tks:
                tks.add(name)
                q.put(name)

        while not q.empty():
            t = q.get()
            for d in self.tasks[t].deps:
                if d in self.tasks and d not in tks:
                    tks.add(d)
                    q.put(d)

        logger.debug(f"Build pipeline for tasks: {tks}.")

        graph = {}

        for key in tks:
            graph[key] = {d for d in self.tasks[key].deps}

        tasks = list((self.tasks[name]
                     for name in TopologicalSorter(graph).static_order()))

        logger.debug(f"Tasks to run: {', '.join((t.name for t in tasks))}")

        return PipelineRunner(tasks, {k: v for k, v in self.hooks.items() if k in tks}, self.phook)
