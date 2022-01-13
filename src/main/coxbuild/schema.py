from dataclasses import asdict
import functools
from typing import Any, Callable
from coxbuild.configuration import Configuration

from coxbuild.pipelines import Pipeline, TaskHook
from coxbuild.tasks import Task, TaskResult
from coxbuild.invocation import CommandExecutionResult, run as inrun, CommandExecutionArgs
import pathlib

pipeline = Pipeline()
config = Configuration()

TaskFuncDecorator = Callable[[Callable[..., None]], Task]


def task(name: str = "") -> TaskFuncDecorator:
    def decorator(body: Callable[..., None]) -> Task:
        if name == "" or name.endswith(":"):
            tname = name + body.__name__
        else:
            tname = name

        tk = Task(tname, body)

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


def before(name: str | Task):
    def decorator(body: Callable[..., None]) -> Callable[..., None]:
        tname = name if isinstance(name, str) else name.name
        if tname in pipeline.hooks:
            old = asdict(pipeline.hooks[tname])
            old.update(before=body)
            hk = TaskHook(**old)
        else:
            hk = TaskHook(before=body)
        pipeline.hook(tname, hk)
        return body
    return decorator


def after(name: str | Task):
    def decorator(body: Callable[..., None]) -> Callable[..., None]:
        tname = name if isinstance(name, str) else name.name
        if tname in pipeline.hooks:
            old = asdict(pipeline.hooks[tname])
            old.update(after=body)
            hk = TaskHook(**old)
        else:
            hk = TaskHook(after=body)
        pipeline.hook(tname, hk)
        return body
    return decorator


def args(name: str | Task):
    def decorator(body: Callable[[], list[Any]]) -> Callable[[], list[Any]]:
        tname = name if isinstance(name, str) else name.name
        if tname in pipeline.hooks:
            old = asdict(pipeline.hooks[tname])
            old.update(args=body)
            hk = TaskHook(**old)
        else:
            hk = TaskHook(args=body)
        pipeline.hook(tname, hk)
        return body
    return decorator


def kwds(name: str | Task):
    def decorator(body: Callable[[], dict[str, Any]]) -> Callable[[], dict[str, Any]]:
        tname = name if isinstance(name, str) else name.name
        if tname in pipeline.hooks:
            old = asdict(pipeline.hooks[tname])
            old.update(kwds=body)
            hk = TaskHook(**old)
        else:
            hk = TaskHook(kwds=body)
        pipeline.hook(tname, hk)
        return body
    return decorator


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: float | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    return inrun(CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe), retry=retry, fail=fail)
