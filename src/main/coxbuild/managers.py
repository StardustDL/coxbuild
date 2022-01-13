import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from graphlib import TopologicalSorter
from queue import Queue
from timeit import default_timer as timer
from typing import Any, Callable, Tuple

from coxbuild.exceptions import CoxbuildException
from coxbuild.runner import Runner
from coxbuild.tasks import Task, TaskResult

logger = logging.getLogger("manager")


class Manager:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        if task.name in self.tasks:
            raise CoxbuildException(
                f"Register multiple task with the same name {task.name}.")
        self.tasks[task.name] = task
        logger.debug(f"Register task {task.name}")

    def __call__(self, *args: Any, **kwds: Any) -> Runner:
        tks = set()
        q: Queue[str] = Queue()
        for name in args:
            if name in self.tasks and name not in tks:
                tks.add(name)
                q.put(name)
        while not q.empty():
            t = q.get()
            for d in self.tasks[t].deps:
                if d in self.tasks and d not in tks:
                    tks.add(d)
                    q.put(d)

        graph = {}

        for key in tks:
            graph[key] = {d for d in self.tasks[key].deps}

        tasks = list((self.tasks[name]
                     for name in TopologicalSorter(graph).static_order()))

        logger.debug(f"Tasks to run: {', '.join((t.name for t in tasks))}")

        return Runner(tasks)
