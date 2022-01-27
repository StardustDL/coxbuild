import inspect
import logging
import sys
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from graphlib import TopologicalSorter
from queue import Queue
from typing import Any, Awaitable, Callable

from coxbuild.hooks import Hook

from .exceptions import CoxbuildException
from .runners import Runner
from .tasks import Task, TaskContext, TaskHook, TaskResult

logger = logging.getLogger("pipelines")


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
class PipelineHook(Hook):
    """Hooks for a pipeline."""
    pass


@dataclass
class PipelineBeforeTaskHook(PipelineHook):
    """Before task starting"""
    hook: Callable[[TaskContext], Awaitable[bool] | bool] | None = None


@dataclass
class PipelineBeforeHook(PipelineHook):
    """Before pipeline starting"""
    hook: Callable[[PipelineContext], Awaitable[bool] | bool] | None = None


@dataclass
class PipelineAfterHook(PipelineHook):
    """After pipeline finished"""
    hook: Callable[[PipelineContext, PipelineResult],
                   Awaitable | None] | None = None


@dataclass
class PipelineAfterTaskHook(PipelineHook):
    """After task finished"""
    hook: Callable[[TaskContext, TaskResult], Awaitable | None] | None = None


def beforePipeline(hook: Callable[[PipelineContext], Awaitable[bool]] | PipelineBeforeHook) -> PipelineBeforeHook:
    """
    Decorator to configure before hook of a task.
    Run before pipeline.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineBeforeHook) else PipelineBeforeHook(hook)


def afterPipeline(hook: Callable[[PipelineContext, PipelineResult], Awaitable[bool]] | PipelineAfterHook) -> PipelineAfterHook:
    """
    Decorator to configure after hook of a task.
    Run after pipeline.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineAfterHook) else PipelineAfterHook(hook)


def beforeTask(hook: Callable[[TaskContext], Awaitable[bool]] | PipelineBeforeTaskHook) -> PipelineBeforeTaskHook:
    """
    Decorator to configure before task hook of a task.
    Run before task.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineBeforeTaskHook) else PipelineBeforeTaskHook(hook)


def afterTask(hook: Callable[[TaskContext, TaskResult], Awaitable[bool]] | PipelineAfterTaskHook) -> PipelineAfterTaskHook:
    """
    Decorator to configure after task hook of a task.
    Run after task.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineAfterTaskHook) else PipelineAfterTaskHook(hook)


class PipelineRunner(Runner):
    """Runner for pipeline."""

    def __init__(self, tasks: list[Task], hooks: list[PipelineHook]) -> None:
        """
        Create runner.

        tasks: tasks in the pipeline
        hooks: hooks for pipeline
        """
        self.tasks = tasks
        self.beforeTask = [beforeTask for beforeTask in hooks if isinstance(
            beforeTask, PipelineBeforeTaskHook)]
        self.afterTask = [afterTask for afterTask in hooks if isinstance(
            afterTask, PipelineAfterTaskHook)]
        self.before = [before for before in hooks if isinstance(
            before, PipelineBeforeHook)]
        self.after = [after for after in hooks if isinstance(
            after, PipelineAfterHook)]
        self.context = PipelineContext(self.tasks)
        self.result = None

        super().__init__(self._run)

    async def _before(self):
        logger.debug(f"Run pipeline before hook")
        for hook in self.before:
            pre = hook.hook(self.context)
            if inspect.isawaitable(pre):
                pre: bool = await pre

            if pre == False:
                return False

    async def _beforeTask(self, context: TaskContext):
        logger.debug(f"Run pipeline before task hook for {context.task.name}")
        for hook in self.beforeTask:
            pre = hook.hook(context)
            if inspect.isawaitable(pre):
                pre: bool = await pre
            if pre == False:
                return False

    async def _afterTask(self, context: TaskContext, result: TaskResult):
        logger.debug(f"Run pipeline after task hook for {context.task.name}")
        for hook in self.afterTask:
            res = hook.hook(context, result)
            if inspect.isawaitable(res):
                await res

    async def _after(self):
        logger.debug(f"Pipeline after hook.")
        for hook in self.after:
            res = hook.hook(self.context, self.result)
            if inspect.isawaitable(res):
                await res

    async def _run(self):
        n = len(self.tasks)

        for i, task in enumerate(self.tasks):
            logger.debug(f"Run task {i+1}({task.name}) of {n} tasks")
            print(f"{'-'*15} ({i+1}/{n}) 📜 Task {task.name} {'-'*15}")
            print("")

            tcontext = TaskContext(task)

            pre = await self._beforeTask(tcontext)
            if pre == False:
                message = f"Stop task {task.name} running by pipeline before hook"
                logger.info(message)
                print(message)
                continue

            res: TaskResult = await task(*tcontext.args, **tcontext.kwds)

            self._results.append(res)

            await self._afterTask(tcontext, res)

            print("")

            if not res:
                break

    async def __aenter__(self) -> Callable[[], Awaitable | None]:
        logger.debug(f"Running pipeline: {self.tasks}")
        print(f"{'-'*20} ⌛ Running 🕰️ {datetime.now()} {'-'*20}")

        self.result = None
        self._results: list[TaskResult] = []

        res = await super().__aenter__()

        pre = await self._before()
        if pre == False:
            message = "Stop pipeline running by pipeline setup hook"
            logger.info(message)
            print(message)
            res = None

        print("")

        return res or (lambda: None)

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

        await self._after()

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
        self.hooks: list[PipelineHook] = []
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

    def hook(self, hook: PipelineHook) -> None:
        """
        Hook pipeline.

        thook: the hook
        """

        self.hooks.append(hook)

    def beforeTask(self, body: Callable[[TaskContext], Awaitable[bool] | bool] | PipelineBeforeTaskHook) -> PipelineBeforeTaskHook:
        """Add before task hook."""
        hook = beforeTask(body)
        self.hook(hook)
        return hook

    def afterTask(self, body: Callable[[TaskContext, TaskResult], Awaitable[bool] | bool] | PipelineAfterTaskHook) -> PipelineAfterTaskHook:
        """Add after task hook."""
        hook = afterTask(body)
        self.hook(hook)
        return hook

    def before(self, body: Callable[[PipelineContext], Awaitable[bool] | bool] | PipelineBeforeHook) -> PipelineBeforeHook:
        """Add before hook."""
        hook = beforePipeline(body)
        self.hook(hook)
        return hook

    def after(self, body: Callable[[PipelineContext, PipelineResult], Awaitable[bool] | bool] | PipelineAfterHook) -> PipelineAfterHook:
        """Add after hook."""
        hook = afterPipeline(body)
        self.hook(hook)
        return hook

    def __call__(self, *args: str | Task, **kwds: Any):
        """
        Build runner of pipeline.

        args: list of tasks or task names
        """

        logger.debug(f"Build pipeline by {args}.")

        unmatchedNames = []

        tks: set[str] = set()
        q: Queue[str] = Queue()
        for name in args:
            if isinstance(name, Task):
                name = name.name
            if name in self.tasks:
                if name not in tks:
                    tks.add(name)
                    q.put(name)
            else:
                unmatchedNames.append(name)

        from .schema import executionState
        executionState.unmatchedTasks = unmatchedNames

        if len(unmatchedNames) > 0:
            message = f"Not found task names: {unmatchedNames}"
            logger.warning(message)
            print(message)

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

        return PipelineRunner(tasks, self.hooks)
