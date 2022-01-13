import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from timeit import default_timer as timer
from tracemalloc import Traceback
from typing import Any, Callable, Tuple


class Runner:
    def __init__(self, func: Callable[[], None]) -> None:
        self.func = func
        self.duration = timedelta()
        self.exc_type = None
        self.exc_value = None
        self.exc_tb = None

    def __enter__(self) -> Callable[[], None]:
        self._tic = timer()

        return self.func

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_tb = exc_tb

        self.duration = timedelta(seconds=timer()-self._tic)

        del self._tic
        return True

