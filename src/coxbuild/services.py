import asyncio
import inspect
import logging
import sys
import traceback
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable

from coxbuild.configuration import Configuration
from coxbuild.exceptions import CoxbuildException
from coxbuild.runners import Runner
from coxbuild.runtime import ExecutionState
from coxbuild.tasks import Task, named, task

if TYPE_CHECKING:
    from .extensions import Extension

logger = logging.getLogger("services")


@dataclass
class EventContext:
    """Event occur information."""
    args: list[Any] = field(default_factory=list)
    """arguments"""
    kwds: dict[str, Any] = field(default_factory=dict)
    """keyword arguments"""

    @classmethod
    def build(cls, *args: Any, **kwds: Any) -> "EventContext":
        return EventContext(args, kwds)


EventType = AsyncIterator[EventContext | None]


@dataclass
class EventHandler:
    """Handler for a event."""
    event: EventType
    """event generator, when the event occurs, the awaitable return"""
    handler: Task
    """event handler"""
    safe: bool = False
    """prevent exception"""
    name: str = ""
    """handler name"""
    extension: "Extension | None" = None

    async def handle(self, config: Configuration | None = None):
        logger.debug(f"Handle for event: {self.name}.")

        config = config or Configuration()
        executionState = ExecutionState(config)

        try:
            async for context in self.event:
                oldhandler = executionState.handler
                oldevent = executionState.event

                executionState.handler = self
                executionState.event = context

                logger.debug(f"Event occurs: {self.name}({context}).")

                logger.debug(f"Event handling: {self.name}({context}).")

                try:
                    runner = self.handler(
                        *context.args, **context.kwds) if context else self.handler()
                    runner.context.config = config
                    result = await runner
                except Exception as ex:
                    if self.safe:
                        print(
                            f"Exception when event handler handling {self.name}({context}).")
                        traceback.print_exception(ex, file=sys.stdout)
                    else:
                        raise CoxbuildException(
                            f"Exception when event handler handling {self.name}({context})", ex)
                finally:
                    executionState.handler = oldhandler
                    executionState.event = oldevent

                logger.debug(f"Event handled: {self.name}({context}).")
        except Exception as ex:
            logger.error(
                f"Event handler '{self.name}' failed.", exc_info=ex)

            if self.safe:
                print(f"Exception in event handler {self.name}.")
                traceback.print_exception(ex, file=sys.stdout)
            else:
                raise CoxbuildException(
                    f"Exception in event handler {self.name}", ex)

        logger.debug(f"Finish handle for event: {self.name}.")


@dataclass
class Service:
    """Event-based service."""

    handlers: list[EventHandler] = field(default_factory=list)
    """handlers in the service"""

    def copy(self) -> "Service":
        """Copy the service."""
        return Service(self.handlers.copy())

    def register(self, handler: EventHandler):
        """Register handler."""
        self.handlers.append(handler)
        logger.debug(f"Register event handler: {handler}")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return ServiceRunner(self)


@dataclass
class ServiceContext:
    """Service context."""
    service: Service
    """service"""
    config: Configuration | None = None
    """configuration"""


class ServiceRunner(Runner):
    def __init__(self, service: Service) -> None:
        self.service = service
        self.context = ServiceContext(self.service)
        super().__init__(self._run)

    async def _run(self):
        logger.debug("Run service.")
        await asyncio.gather(*[e.handle(self.context.config) for e in self.service.handlers])
        logger.debug("Finish service.")


def on(event: Callable[[], Awaitable], safe: bool = False, name: str | None = None):
    """
    Decorator to register event handler.

    event: event generator, when the event occurs, the awaitable return
    handler: event handler
    repeat: repeat times, 0 for no-repeat, positive integer for finite repeat, negative integer for infinite repeat
    safe: prevent exception
    name: handler name, None to use function name
    """
    def decorator(handler: Callable[[], None] | Task):
        tname = name or handler.__name__
        if not isinstance(handler, Task):
            handler = named(tname)(task(handler))

        return EventHandler(event, handler, safe, tname)

    return decorator
