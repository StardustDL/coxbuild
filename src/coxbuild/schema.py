import pathlib
from dataclasses import asdict
from datetime import timedelta
from typing import Awaitable, Callable

from .configuration import Configuration
from .invocation import CommandExecutionArgs, CommandExecutionResult
from .invocation import run as inrun
from .pipelines import (Pipeline, PipelineContext, PipelineHook,
                        PipelineResult, TaskContext, TaskHook)
from .services import EventHandler, Service
from .tasks import Task, TaskResult

service = Service()
pipeline = Pipeline()
config = Configuration()

TaskFuncDecorator = Callable[[Callable[..., None]], Task]


def task(name: str = "") -> TaskFuncDecorator:
    """
    Define a task.

    name: use custom task name, empty to use function name.
    """
    def decorator(body: Callable[..., None]) -> Task:
        # endswith(":") support empty name with group name
        if name == "" or name.endswith(":"):
            tname = name + body.__name__
        else:
            tname = name

        tk = Task(tname, body, body.__doc__ or "")

        pipeline.register(tk)
        return tk
    return decorator


def depend(*names: str | Task):
    """
    Define dependencies of a task.

    names: task names or task instances
    """
    def decorator(inner: Task) -> Task:
        for name in names:
            inner.deps.append(name if isinstance(name, str) else name.name)
        return inner
    return decorator


def group(name: str, inner: Callable[[str], TaskFuncDecorator] | None = None):
    """
    Add namespace to task names (prevent from name conflicting).

    name: group name
    inner: inner task definer (for nested group)
    """

    if inner is None:
        inner = task

    def wrapper(subname: str = "") -> TaskFuncDecorator:
        return inner(f"{name}:{subname}")
    return wrapper


def precond(predicate: Callable[..., bool]):
    """
    Configure precondition of the task.
    Decide whether to run the task.

    predicate: condition tester
    """
    def decorator(inner: Task) -> Task:
        inner.precondition = predicate
        return inner
    return decorator


def postcond(predicate: Callable[..., bool]):
    """
    Configure postcondition of the task.
    Check the task works well.

    predicate: condition tester
    """
    def decorator(inner: Task) -> Task:
        inner.postcondition = predicate
        return inner
    return decorator


def invoke(name: str | Task, /, *args, **kwds) -> TaskResult:
    """Invoke a task by name or instance."""
    if isinstance(name, str):
        name = pipeline.tasks[name]

    return name(*args, **kwds)


def before(name: str | Task | None = None):
    """
    Configure before hook.

    name: task instance or name, None for pipeline hook
    """
    def decorator(body: Callable[[TaskContext], bool]):
        if name:
            tname = name if isinstance(name, str) else name.name
            if tname in pipeline.hooks:
                old = asdict(pipeline.hooks[tname])
                old.update(before=body)
                hk = TaskHook(**old)
            else:
                hk = TaskHook(before=body)
            pipeline.hook(hk, tname)
        else:
            old = asdict(pipeline.phook)
            old.update(before=body)
            hk = PipelineHook(**old)
            pipeline.hook(hk)
        return body
    return decorator


def after(name: str | Task | None = None):
    """
    Configure after hook.

    name: task instance or name, None for pipeline hook
    """
    def decorator(body: Callable[[TaskContext, TaskResult], None]):
        if name:
            tname = name if isinstance(name, str) else name.name
            if tname in pipeline.hooks:
                old = asdict(pipeline.hooks[tname])
                old.update(after=body)
                hk = TaskHook(**old)
            else:
                hk = TaskHook(after=body)
            pipeline.hook(hk, tname)
        else:
            old = asdict(pipeline.phook)
            old.update(after=body)
            hk = PipelineHook(**old)
            pipeline.hook(hk)
        return body
    return decorator


def setup(name: str | Task | None = None):
    """
    Configure setup hook.

    name: task instance or name, None for pipeline hook
    """
    def decorator(body: Callable[..., None] | Callable[[PipelineContext], bool]):
        if name:
            tname = name if isinstance(name, str) else name.name
            if tname in pipeline.hooks:
                old = asdict(pipeline.hooks[tname])
                old.update(setup=body)
                hk = TaskHook(**old)
            else:
                hk = TaskHook(setup=body)
            pipeline.hook(hk, tname)
        else:
            old = asdict(pipeline.phook)
            old.update(setup=body)
            hk = PipelineHook(**old)
            pipeline.hook(hk)
        return body
    return decorator


def teardown(name: str | Task | Task | None = None):
    """
    Configure teardown hook.

    name: task instance or name, None for pipeline hook
    """
    def decorator(body: Callable[..., None] | Callable[[PipelineContext, PipelineResult], None]):
        if name:
            tname = name if isinstance(name, str) else name.name
            if tname in pipeline.hooks:
                old = asdict(pipeline.hooks[tname])
                old.update(teardown=body)
                hk = TaskHook(**old)
            else:
                hk = TaskHook(teardown=body)
            pipeline.hook(hk, tname)
        else:
            old = asdict(pipeline.phook)
            old.update(teardown=body)
            hk = PipelineHook(**old)
            pipeline.hook(hk)
        return body
    return decorator


def on(event: Callable[[], Awaitable], safe: bool = False, name: str | None = None):
    """
    Register event handler.

    event: event generator, when the event occurs, the awaitable return
    handler: event handler
    repeat: repeat times, 0 for no-repeat, positive integer for finite repeat, negative integer for infinite repeat
    safe: prevent exception
    name: handler name, None to use function name
    """
    def decorator(handler: Callable[[], None]):
        service.register(EventHandler(event, handler,
                         safe, name or handler.__name__))
        return handler

    return decorator


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: timedelta | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    """
    Run command.

    cmds: command and argument
    env: environ
    cwd: current working directory
    timeout: maximum execution duration
    input: text for stdin
    shell: use system shell
    pipe: pipe and collect stdout and stderr
    retry: the number of times to retry when failing
    fail: do not raise exception when the final result fails
    """
    return inrun(CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe), retry=retry, fail=fail)
