import inspect
import logging
import sys
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from graphlib import TopologicalSorter
from queue import Queue
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from coxbuild.configurations import Configuration
from coxbuild.hooks import Hook
from coxbuild.runtime import ExecutionState

from .exceptions import CoxbuildRuntimeException, CoxbuildSchemaException
from .runners import Runner
from .tasks import Task, TaskContext, TaskHook, TaskResult

if TYPE_CHECKING:
    from .extensions import Extension

logger = logging.getLogger("pipelines")


class PipelineRuntimeException(CoxbuildRuntimeException):
    """Exception for pipeline running."""
    pass


@dataclass
class PipelineContext:
    """Execution context for pipeline."""
    pipeline: "Pipeline"
    """pipeline"""
    tasks: list[TaskResult]
    """tasks in the pipeline"""
    unmatchedNames: list[str] = field(default_factory=list)
    """not found task names"""
    config: Configuration | None = None
    """configuration"""


@dataclass
class PipelineResult:
    """Execution result for pipeline."""
    duration: timedelta
    """execution duration"""
    tasks: list[TaskResult]
    """tasks in the pipeline"""
    exception: PipelineRuntimeException | None = None
    """exception when running"""

    def __bool__(self):
        return self.exception is None and all((t for t in self.tasks if not t.task.continueOnError))

    @property
    def description(self) -> str:
        """Return result's description string."""
        return "🟢 SUCCESS" if self else "🔴 FAILING"


@dataclass
class PipelineHook(Hook):
    """Hooks for a pipeline."""
    extension: "Extension | None" = None


@dataclass
class PipelineBeforeTaskHook(PipelineHook):
    """Before task starting"""
    hook: Callable[[TaskContext], Awaitable[bool] | bool | None] | None = None


@dataclass
class PipelineBeforeHook(PipelineHook):
    """Before pipeline starting"""
    hook: Callable[[PipelineContext],
                   Awaitable[bool] | bool | None] | None = None


@dataclass
class PipelineAfterHook(PipelineHook):
    """After pipeline finished"""
    hook: Callable[[PipelineContext, PipelineResult],
                   Awaitable | None] | None = None


@dataclass
class PipelineAfterTaskHook(PipelineHook):
    """After task finished"""
    hook: Callable[[TaskContext, TaskResult], Awaitable | None] | None = None


def beforePipeline(hook: Callable[[PipelineContext], Awaitable[bool] | bool | None] | PipelineBeforeHook) -> PipelineBeforeHook:
    """
    Decorator to configure before hook of a pipeline.
    Run before pipeline.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineBeforeHook) else PipelineBeforeHook(hook)


def afterPipeline(hook: Callable[[PipelineContext, PipelineResult], Awaitable | None] | PipelineAfterHook) -> PipelineAfterHook:
    """
    Decorator to configure after hook of a pipeline.
    Run after pipeline.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineAfterHook) else PipelineAfterHook(hook)


def beforeTask(hook: Callable[[TaskContext], Awaitable[bool] | bool | None] | PipelineBeforeTaskHook) -> PipelineBeforeTaskHook:
    """
    Decorator to configure before task hook of a task.
    Run before task.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineBeforeTaskHook) else PipelineBeforeTaskHook(hook)


def afterTask(hook: Callable[[TaskContext, TaskResult], Awaitable | None] | PipelineAfterTaskHook) -> PipelineAfterTaskHook:
    """
    Decorator to configure after task hook of a task.
    Run after task.

    hook: hook function
    """
    return hook if isinstance(hook, PipelineAfterTaskHook) else PipelineAfterTaskHook(hook)


class PipelineRunner(Runner):
    """Runner for pipeline."""

    def __init__(self, pipeline: "Pipeline", tasks: list[Task], hooks: list[PipelineHook], unmatchedNames: list[str]) -> None:
        """
        Create runner.

        pipeline: pipeline
        tasks: tasks in the pipeline
        hooks: hooks for pipeline
        unmatchedNames: not found task names
        """
        self.pipeline = pipeline
        self.tasks = tasks
        self.beforeTask = [beforeTask for beforeTask in hooks if isinstance(
            beforeTask, PipelineBeforeTaskHook)]
        self.afterTask = [afterTask for afterTask in hooks if isinstance(
            afterTask, PipelineAfterTaskHook)]
        self.before = [before for before in hooks if isinstance(
            before, PipelineBeforeHook)]
        self.after = [after for after in hooks if isinstance(
            after, PipelineAfterHook)]
        self.context = PipelineContext(
            self.pipeline, self.tasks, unmatchedNames)
        self.result = None

        super().__init__(self._run)

    async def _before(self):
        logger.debug(f"Run pipeline before hook")
        try:
            for hook in self.before:
                pre = hook.hook(self.context)
                if inspect.isawaitable(pre):
                    pre: bool = await pre

                if pre == False:
                    return False
        except Exception as ex:
            logger.error(f"Run pipeline before hook failed.", exc_info=ex)
            print(f"Run pipeline before hook failed: {ex}")
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
        try:
            for hook in self.after:
                res = hook.hook(self.context, self.result)
                if inspect.isawaitable(res):
                    await res
        except Exception as ex:
            logger.error(f"Run pipeline after hook failed.", exc_info=ex)
            print(f"Run pipeline after hook failed: {ex}")

    async def _run(self):
        n = len(self.tasks)

        for i, task in enumerate(self.tasks):
            logger.debug(f"Run task {i+1}({task.name}) of {n} tasks")
            print(f"{'-'*15} ({i+1}/{n}) 📜 Task {task.name} {'-'*15}")
            print("")

            self._executionState.task = task

            runner = task()
            runner.context.config = self.context.config

            pre = await self._beforeTask(runner.context)
            if pre == False:
                message = f"Stop task {task.name} running by pipeline before hook"
                logger.info(message)
                print(message)
                continue

            res = await runner

            self._results.append(res)

            await self._afterTask(runner.context, res)

            self._executionState.task = None

            if not res:
                if task.continueOnError:
                    message = f"Task {task.name} failed, but continue on error."
                    logger.error(message)
                    print(message)
                    print("")
                else:
                    print("")
                    break

    async def __aenter__(self) -> Callable[[], Awaitable | None]:
        logger.debug(f"Running pipeline: {self.tasks}")
        print(f"{'-'*20} ⌛ Running 🕰️ {datetime.now()} {'-'*20}")

        self.result = None
        self._results: list[TaskResult] = []

        self.context.config = self.context.config or Configuration()
        self._executionState = ExecutionState(self.context.config)
        self._executionState.matchedTasks = self.tasks
        self._executionState.unmatchedTasks = self.context.unmatchedNames

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

        exception = None if self.exc_value is None else PipelineRuntimeException(
            f"Failed to run pipeline", cause=self.exc_value)
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
            print(
                f"({i+1}/{cnt})\t{tr.description}\t⏱️ {tr.duration}\t📜 {tr.task.name}")

        del self._results
        del self._executionState

        return True

    def __await__(self):
        yield from super().__await__()
        return self.result


@dataclass
class Pipeline:
    """Pipeline to run tasks."""

    tasks: dict[str, Task] = field(default_factory=dict)
    """tasks in the pipeline"""
    hooks: list[PipelineHook] = field(default_factory=list)
    """hook for pipeline"""

    def copy(self) -> "Pipeline":
        """Copy pipeline."""
        return Pipeline(tasks=self.tasks.copy(), hooks=self.hooks.copy())

    def register(self, task: Task) -> None:
        """
        Register a task into pipeline.

        task: task to register
        """
        if task.name in self.tasks:
            logger.warning(
                f"Replace registered task: {self.tasks[task.name]}.")
        self.tasks[task.name] = task
        logger.debug(f"Register task {task}")

    def hook(self, hook: PipelineHook) -> None:
        """
        Hook pipeline.

        thook: the hook
        """

        self.hooks.append(hook)

    def beforeTask(self, body: Callable[[TaskContext], Awaitable[bool] | bool | None] | PipelineBeforeTaskHook) -> PipelineBeforeTaskHook:
        """Add before task hook."""
        hook = beforeTask(body)
        self.hook(hook)
        return hook

    def afterTask(self, body: Callable[[TaskContext, TaskResult], Awaitable[bool] | bool | None] | PipelineAfterTaskHook) -> PipelineAfterTaskHook:
        """Add after task hook."""
        hook = afterTask(body)
        self.hook(hook)
        return hook

    def before(self, body: Callable[[PipelineContext], Awaitable[bool] | bool | None] | PipelineBeforeHook) -> PipelineBeforeHook:
        """Add before hook."""
        hook = beforePipeline(body)
        self.hook(hook)
        return hook

    def after(self, body: Callable[[PipelineContext, PipelineResult], Awaitable | None] | PipelineAfterHook) -> PipelineAfterHook:
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

        tks: set[Task] = set()
        q: Queue[Task] = Queue()
        for task in args:
            if isinstance(task, str):
                if task in self.tasks:
                    task = self.tasks[task]
                else:
                    unmatchedNames.append(task)
                    continue
            if task not in tks:
                tks.add(task)
                q.put(task)

        if len(unmatchedNames) > 0:
            message = f"Not found task names: {unmatchedNames}"
            logger.warning(message)
            print(message)

        while not q.empty():
            t = q.get()
            for d in t.deps:
                if d not in tks:
                    tks.add(d)
                    q.put(d)

        logger.debug(f"Build pipeline for tasks: {tks}.")

        graph: dict[Task, set[Task]] = {}

        for key in tks:
            graph[key] = {d for d in key.deps}

        tasks = list((task
                     for task in TopologicalSorter(graph).static_order()))

        logger.debug(f"Tasks to run: {', '.join((t.name for t in tasks))}")

        return PipelineRunner(self, tasks, self.hooks, unmatchedNames)
