import functools
from typing import Callable

from coxbuild.managers import Manager
from coxbuild.tasks import Task

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
