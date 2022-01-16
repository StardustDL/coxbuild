import asyncio
import logging
import sys
import traceback
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Awaitable, Callable
import inspect

from coxbuild.exceptions import CoxbuildException
from coxbuild.runners import Runner

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
    handler: Callable[..., Awaitable | None]
    """event handler"""
    safe: bool = False
    """prevent exception"""
    name: str = ""
    """handler name"""

    async def handle(self):
        logger.debug(f"Handle for event: {self.name}.")

        try:
            async for context in self.event:
                logger.debug(f"Event occurs: {self.name}({context}).")

                logger.debug(f"Event handling: {self.name}({context}).")

                try:
                    result = self.handler(
                        *context.args, **context.kwds) if context else self.handler()
                    if inspect.isawaitable(result):
                        result = await result
                except Exception as ex:
                    if self.safe:
                        print(
                            f"Exception when event handler handling {self.name}({context}).")
                        traceback.print_exception(ex, file=sys.stdout)
                    else:
                        raise CoxbuildException(
                            f"Exception when event handler handling {self.name}({context})", ex)

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


class Service:
    """Event-based service."""

    def __init__(self) -> None:
        self.handlers: list[EventHandler] = []
        """handlers in the service"""

    def register(self, handler: EventHandler):
        """Register handler."""
        logger.debug(f"Register event handler: {handler}")
        self.handlers.append(handler)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return ServiceRunner(self)


class ServiceRunner(Runner):
    def __init__(self, service: Service) -> None:
        self.service = service
        super().__init__(self._run)

    async def _run(self):
        logger.debug("Run service.")
        await asyncio.gather(*[e.handle() for e in self.service.handlers])
        logger.debug("Finish service.")
