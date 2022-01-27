import asyncio
import inspect
import logging
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable

from coxbuild.hooks import Hook

from .exceptions import CoxbuildException
from .runners import Runner

logger = logging.getLogger("tasks")


@dataclass
class TaskContext:
    """Execution context for task."""
    task: "Task"
    """running task"""
    args: list[Any] = field(default_factory=list)
    """arguments"""
    kwds: dict[str, Any] = field(default_factory=dict)
    """keyword arguments"""


@dataclass
class TaskResult:
    """Execution result for task."""
    name: str
    """task name"""
    duration: timedelta
    """execution duration"""
    exception: CoxbuildException | None
    """exception when running"""

    def __bool__(self):
        return self.exception is None

    @property
    def description(self) -> str:
        """Return result's description string."""
        return "🟢 SUCCESS" if self else "🔴 FAILING"

    def ensure(self) -> None:
        """Ensure the result is success, otherwise re-raise exception."""
        if not self:
            raise self.exception


@dataclass
class TaskHook(Hook):
    """Hooks for a task."""
    pass


@dataclass
class TaskBeforeHook(TaskHook):
    """Before task starting"""
    hook: Callable[[TaskContext], Awaitable[bool] | bool] | None = None


@dataclass
class TaskSetupHook(TaskHook):
    """Setup before task running"""
    hook: Callable[..., Awaitable | None] | None = None


@dataclass
class TaskPreconditionHook(TaskHook):
    """Condition to decide whether to run the task"""
    hook: Callable[..., Awaitable[bool] | bool] | None = None


@dataclass
class TaskPostconditionHook(TaskHook):
    """Condition to decide whether to run the task"""
    hook: Callable[..., Awaitable[bool] | bool] | None = None


@dataclass
class TaskTeardownHook(TaskHook):
    """Teardown after task running"""
    hook: Callable[..., Awaitable | None] | None = None


@dataclass
class TaskAfterHook(TaskHook):
    """After task finished"""
    hook: Callable[[TaskContext, TaskResult], Awaitable | None] | None = None


def asprecond(predicate: Callable[..., bool] | TaskPreconditionHook):
    """
    Decorator to define precondition of a task.
    Decide whether to run a task.

    predicate: condition tester
    """
    return predicate if isinstance(predicate, TaskPreconditionHook) else TaskPreconditionHook(predicate)


def aspostcond(predicate: Callable[..., bool] | TaskPostconditionHook):
    """
    Decorator to define postcondition of the task.
    Check the task works well.

    predicate: condition tester
    """
    return predicate if isinstance(predicate, TaskPostconditionHook) else TaskPostconditionHook(predicate)


def asbefore(hook: Callable[[TaskContext], Awaitable[bool]] | TaskBeforeHook):
    """
    Decorator to define before hook of a task.
    Run before task body.

    hook: hook function
    """
    return hook if isinstance(hook, TaskBeforeHook) else TaskBeforeHook(hook)


def asafter(hook: Callable[[TaskContext, TaskResult], Awaitable[bool]] | TaskAfterHook):
    """
    Decorator to define after hook of a task.
    Run after task body.

    hook: hook function
    """
    return hook if isinstance(hook, TaskAfterHook) else TaskAfterHook(hook)


def assetup(hook: Callable[..., Awaitable[None]] | TaskSetupHook):
    """
    Decorator to define setup hook of a task.
    Run before task body.

    hook: hook function
    """
    return hook if isinstance(hook, TaskSetupHook) else TaskSetupHook(hook)


def asteardown(hook: Callable[..., Awaitable[None]] | TaskTeardownHook):
    """
    Decorator to define teardown hook of a task.
    Run after task body.

    hook: hook function
    """
    return hook if isinstance(hook, TaskTeardownHook) else TaskTeardownHook(hook)


@dataclass
class Task:
    """Task."""
    name: str = "default"
    """task name"""
    body: Callable[..., Awaitable | None] | None = None
    """task body"""
    doc: str = ""
    """task document"""
    deps: list[str] = field(default_factory=list)
    """dependency task names"""
    hooks: list[TaskHook] = field(default_factory=list)
    """task hooks"""

    def __call__(self, *args: Any, **kwds: Any) -> TaskResult:
        """
        Build runner of task.

        args: task arguments
        kwds: task keyword arguments
        setup: setup hooks
        teardown: teardown hooks
        """
        return TaskRunner(self, list(args), kwds)

    def depend(self, task: "Task") -> "Task":
        """Add dependency task."""
        self.deps.append(task.name)
        return task

    def hook(self, hook: TaskHook) -> "TaskHook":
        """Add hook."""
        self.hooks.append(hook)
        return hook

    def precond(self, body: Callable[..., Awaitable[bool] | bool] | TaskPreconditionHook) -> TaskPreconditionHook:
        """Add precondition hook."""
        return self.hook(asprecond(body))

    def postcond(self, body: Callable[..., Awaitable[bool] | bool] | TaskPostconditionHook) -> TaskPostconditionHook:
        """Add postcondition hook."""
        return self.hook(aspostcond(body))

    def before(self, body: Callable[[TaskContext], Awaitable[bool] | bool] | TaskBeforeHook) -> TaskBeforeHook:
        """Add before hook."""
        return self.hook(asbefore(body))

    def after(self, body: Callable[[TaskContext, TaskResult], Awaitable | None] | TaskAfterHook) -> TaskAfterHook:
        """Add after hook."""
        return self.hook(asafter(body))

    def setup(self, body: Callable[..., Awaitable | None] | TaskSetupHook) -> TaskSetupHook:
        """Add setup hook."""
        return self.hook(assetup(body))

    def teardown(self, body: Callable[..., Awaitable | None] | TaskTeardownHook) -> TaskTeardownHook:
        """Add teardown hook."""
        return self.hook(asteardown(body))


class TaskRunner(Runner):
    """Runner for task."""

    def __init__(self, task: Task, args: list[Any], kwds: dict[str, Any]) -> None:
        self.context = TaskContext(task, args, kwds)
        self.setup = [setup for setup in task.hooks if isinstance(
            setup, TaskSetupHook)]
        self.teardown = [teardown for teardown in task.hooks if isinstance(
            teardown, TaskTeardownHook)]
        self.before = [before for before in task.hooks if isinstance(
            before, TaskBeforeHook)]
        self.after = [after for after in task.hooks if isinstance(
            after, TaskAfterHook)]
        self.precond = [precond for precond in task.hooks if isinstance(
            precond, TaskPreconditionHook)]
        self.postcond = [postcond for postcond in task.hooks if isinstance(
            postcond, TaskPostconditionHook)]

        super().__init__(self._run)

    async def _before(self):
        logger.debug(f"Run task before hook for {self.context.task.name}")
        for hook in self.before:
            pre = hook.hook(self.context)
            if inspect.isawaitable(pre):
                pre: bool = await pre
            if pre == False:
                return False

    async def _after(self):
        logger.debug(f"Run task after hook for {self.context.task.name}")
        for hook in self.after:
            res = hook.hook(self.context, self.result)
            if inspect.isawaitable(res):
                await res

    async def _setup(self):
        logger.debug(f"Task {self.context.task.name} setup hook.")
        for hook in self.setup:
            af = hook(*self.context.args, **self.context.kwds)
            if inspect.isawaitable(af):
                af = await af

    async def _teardown(self):
        logger.debug(f"Task {self.context.task.name} teardown hook.")
        for hook in self.teardown:
            af = hook(*self.context.args, **self.context.kwds)
            if inspect.isawaitable(af):
                af = await af

    async def _precond(self):
        logger.debug(f"Task {self.context.task.name} check precondition.")
        for hook in self.precond:
            pre = hook.hook(*self.context.args, **self.context.kwds)
            if inspect.isawaitable(pre):
                pre: bool = await pre

            if not pre:
                return pre
        return True

    async def _postcond(self):
        logger.debug(f"Task {self.context.task.name} check postcondition.")
        for hook in self.postcond:
            post = hook.hook(*self.context.args, **self.context.kwds)
            if inspect.isawaitable(post):
                post: bool = await post

            if not post:
                return post
        return True

    async def _run(self):
        pre = await self._precond()
        if not pre:
            message = f"Task {self.context.task.name} ignored: precondition filtered"
            logger.info(message)
            print(message)
            return

        await self._setup()

        try:
            if self.context.task.body is not None:
                logger.debug(f"Task {self.context.task.name} body execute.")
                af = self.context.task.body(
                    *self.context.args, **self.context.kwds)
                if inspect.isawaitable(af):
                    af = await af
        finally:
            await self._teardown()

        post = await self._postcond()
        if not post:
            raise CoxbuildException(
                f"Task {self.context.task.name} failed: postcondition checking broken")

    async def __aenter__(self) -> Callable[[], Awaitable | None]:
        logger.debug(f"Start task {self.context.task.name}.")
        print(f"{'-'*3} 🔻 {self.context.task.name} 🕰️ {datetime.now()} {'-'*3}")

        self.result = None

        res = await super().__aenter__()

        pre = await self._before()

        if pre == False:
            message = f"Stop task {self.context.task.name} running by task before hook"
            logger.info(message)
            print(message)
            res = None

        return res or (lambda: None)

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> bool:
        await super().__aexit__(exc_type, exc_value, exc_tb)

        exception = None if self.exc_value is None else CoxbuildException(
            f"Failed to run task: {self.context.task.name}", cause=self.exc_value)
        self.result = TaskResult(
            self.context.task.name, duration=self.duration, exception=exception)

        if self.exc_value is not None:
            logger.error("Task execute exception.", exc_info=self.exc_value)
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_tb, file=sys.stdout)

        await self._after()

        logger.debug(f"Finish task {self.context.task.name}: {self.result}.")

        print(
            f"{'-'*3} 🔺 {self.context.task.name} {self.result.description} ⏱️ {self.result.duration} {'-'*3}")

        return True

    def __await__(self):
        yield from super().__await__()
        return self.result


TaskFuncDecorator = Callable[[Callable[..., None]], Task]


def task(body: Callable[..., None]) -> Task:
    """
    Decorator to define a task.
    """
    tk = Task(body.__name__, body, body.__doc__ or "")
    return tk


def named(name: str):
    """
    Decorator to set task name.
    """
    def decorator(inner: Task) -> Task:
        inner.name = name
        return inner
    return decorator


def group(name: str, parent: Callable[[Task], Task] | None = None):
    """
    Decorator to set task group.
    """
    def decorator(inner: Task) -> Task:
        inner.name = f"{name}:{inner.name}"
        if parent:
            inner = parent(inner)
        return inner
    return decorator


def depend(*names: str | Task):
    """
    Decorator to define dependencies of a task.

    names: task names or task instances
    """
    def decorator(inner: Task) -> Task:
        for name in names:
            inner.deps.append(name if isinstance(name, str) else name.name)
        return inner
    return decorator


def precond(hook: Callable[..., Awaitable[bool] | bool] | TaskPreconditionHook):
    """
    Decorator to configure precondition hook of the task.
    """
    def decorator(inner: Task) -> Task:
        inner.precond(hook)
        return inner
    return decorator


def postcond(hook: Callable[..., Awaitable[bool] | bool] | TaskPostconditionHook):
    """
    Decorator to configure postcondition hook of the task.
    """
    def decorator(inner: Task) -> Task:
        inner.postcond(hook)
        return inner
    return decorator


def before(hook: Callable[[TaskContext], Awaitable[bool] | bool] | TaskBeforeHook):
    """
    Decorator to configure before hook of the task.
    """
    def decorator(inner: Task) -> Task:
        inner.before(hook)
        return inner
    return decorator


def after(hook: Callable[[TaskContext, TaskResult], Awaitable | None] | TaskAfterHook):
    """
    Decorator to configure after hook of the task.
    """
    def decorator(inner: Task) -> Task:
        inner.after(hook)
        return inner
    return decorator


def setup(hook: Callable[..., Awaitable | None] | TaskSetupHook):
    """
    Decorator to configure setup hook of the task.
    """
    def decorator(inner: Task) -> Task:
        inner.setup(hook)
        return inner
    return decorator


def teardown(hook: Callable[..., Awaitable | None] | TaskTeardownHook):
    """
    Decorator to configure teardown hook of the task.
    """
    def decorator(inner: Task) -> Task:
        inner.teardown(hook)
        return inner
    return decorator
