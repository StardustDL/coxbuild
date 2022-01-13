import functools
from typing import Callable

from coxbuild.managers import Manager
from coxbuild.tasks import Task
import pathlib

manager = Manager()


def task(name: str = ""):
    def decorator(body: Callable[[], None]) -> Task:
        tk = Task(name if name else body.__name__, body)

        manager.register(tk)
        return tk
    return decorator


def depend(*names: str | Task):
    def decorator(inner: Task) -> Task:
        for name in names:
            inner.deps.append(name if isinstance(name, str) else name.name)
        return inner
    return decorator


def run(cmds: list[str], env: dict[str, str] | None = None,
        cwd: pathlib.Path | None = None, timeout: float | None = None,
        input: str | None = None,
        shell: bool = False, pipe: bool = False,
        retry: int = 0, fail: bool = False):
    from coxbuild import invocation
    return invocation.run(invocation.CommandExecutionArgs(cmds, env, cwd, timeout, input, shell, pipe), retry=retry, fail=fail)
