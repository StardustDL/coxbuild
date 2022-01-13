import functools
from typing import Callable

from coxbuild.managers import Manager
from coxbuild.tasks import Task, TaskResult
import pathlib

manager = Manager()

TaskFuncDecorator = Callable[[Callable[..., None]], Task]


def task(name: str = "") -> TaskFuncDecorator:
    def decorator(body: Callable[..., None]) -> Task:
        tk = Task(name if name else body.__name__, body)

        manager.register(tk)
        return tk
    return decorator


def grouptask(name: str, inner: Callable[[str], TaskFuncDecorator] | None = None):
    if inner is None:
        inner = task

    def wrapper(subname: str) -> TaskFuncDecorator:
        return inner(f"{name}:{subname}")
    return wrapper


def depend(*names: str | Task):
    def decorator(inner: Task) -> Task:
        for name in names:
            inner.deps.append(name if isinstance(name, str) else name.name)
        return inner
    return decorator


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


def invoke(name: str | Task, *args, **kwds) -> TaskResult:
    if isinstance(name, str):
        name = manager.tasks[name]

    return name.invoke(*args, **kwds)


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: float | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False):
    from coxbuild import invocation
    return invocation.run(invocation.CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe), retry=retry, fail=fail)
