from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Hook:
    """Hook."""
    hook: Callable

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.hook(*args, **kwds)
