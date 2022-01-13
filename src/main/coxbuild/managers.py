from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Tuple
from timeit import default_timer as timer
from coxbuild.exceptions import CoxbuildException
from coxbuild.tasks import Task, TaskResult
from graphlib import TopologicalSorter
from queue import Queue


@dataclass
class RunnerResult:
    duration: timedelta
    tasks: list[TaskResult]
    exception: CoxbuildException | None = None

    def __bool__(self):
        return self.exception is None and all(self.tasks)


class Runner:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks
        self.result = None

    def __enter__(self) -> Callable[[], None]:
        print(f"{'-'*5} Running @ {datetime.now()} {'-'*5}")

        self.result = None
        self._tic = timer()
        self._results: list[TaskResult] = []

        def runner():
            for task in self.tasks:
                with task as run:
                    run()
                self._results.append(task.result)

        return runner

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        exception = None if exc_value is None else CoxbuildException(
            f"Failed to run runner", cause=exc_value)
        duration = timedelta(seconds=timer()-self._tic)
        self.result = RunnerResult(
            duration=duration, tasks=self._results, exception=exception)
        del self._tic
        del self._results

        print(f"{'-'*5} Done ({'SUCCESS' if self.result else 'FAILED'} @ {self.result.duration}) {'-'*5}")

        print(f"{'SUCCESS' if self.result else 'FAILED'} @ {self.result.duration}")
        if self.result.exception:
            print(f"Exception: {self.result.exception}")
        for tr in self.result.tasks:
            print(f"  {tr.name}: {'SUCCESS' if tr else 'FAILED'} @ {tr.duration}")

        return True


class Manager:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        if task.name in self.tasks:
            raise CoxbuildException(
                f"Register multiple task with the same name {task.name}.")
        self.tasks[task.name] = task

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
        
        return Runner(list((self.tasks[name] for name in TopologicalSorter(graph).static_order())))
