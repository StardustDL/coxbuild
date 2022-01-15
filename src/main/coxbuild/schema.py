import functools
import pathlib
from dataclasses import asdict
from typing import Any, Awaitable, Callable

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
    def decorator(body: Callable[..., None]) -> Task:
        if name == "" or name.endswith(":"):
            tname = name + body.__name__
        else:
            tname = name

        tk = Task(tname, body, body.__doc__ or "")

        pipeline.register(tk)
        return tk
    return decorator


def depend(*names: str | Task):
    def decorator(inner: Task) -> Task:
        for name in names:
            inner.deps.append(name if isinstance(name, str) else name.name)
        return inner
    return decorator


def group(name: str, inner: Callable[[str], TaskFuncDecorator] | None = None):
    if inner is None:
        inner = task

    def wrapper(subname: str = "") -> TaskFuncDecorator:
        return inner(f"{name}:{subname}")
    return wrapper


def precond(predicate: Callable[..., bool]):
    def decorator(inner: Task) -> Task:
        inner.precondition = predicate
        return inner
    return decorator


def postcond(predicate: Callable[..., bool]):
    def decorator(inner: Task) -> Task:
        inner.postcondition = predicate
        return inner
    return decorator


def invoke(name: str | Task, /, *args, **kwds) -> TaskResult:
    if isinstance(name, str):
        name = pipeline.tasks[name]

    return name.invoke(*args, **kwds)


def before(name: str | Task | None = None):
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


def on(event: Callable[[], Awaitable], repeat: int = 0):
    def decorator(handler: Callable[[], None]):
        service.register(EventHandler(event, handler, repeat))
        return handler

    return decorator


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: float | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    return inrun(CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe), retry=retry, fail=fail)
