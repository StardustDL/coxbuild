import functools
from typing import Callable
from coxbuild.configuration import Configuration

from coxbuild.managers import Manager
from coxbuild.tasks import Task, TaskResult
from coxbuild.invocation import CommandExecutionResult, run as inrun, CommandExecutionArgs
import pathlib

manager = Manager()
config = Configuration()

TaskFuncDecorator = Callable[[Callable[..., None]], Task]


def task(name: str = "") -> TaskFuncDecorator:
    def decorator(body: Callable[..., None]) -> Task:
        if name == "" or name.endswith(":"):
            tname = name + body.__name__
        else:
            tname = name

        tk = Task(tname, body)

        manager.register(tk)
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
        name = manager.tasks[name]

    return name.invoke(*args, **kwds)


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: float | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False) -> CommandExecutionResult:
    return inrun(CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe), retry=retry, fail=fail)
