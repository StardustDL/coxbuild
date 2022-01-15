import asyncio
import logging
import traceback
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from coxbuild.exceptions import CoxbuildException, EventCannotOccur

logger = logging.getLogger("services")


@dataclass
class EventHandler:
    """Handler for a event."""
    event: Callable[[], Awaitable]
    """event generator, when the event occurs, the awaitable return"""
    handler: Callable[[], None]
    """event handler"""
    repeat: int = 0
    """repeat times, 0 for no-repeat, positive integer for finite repeat, negative integer for infinite repeat"""
    safe: bool = False
    """prevent exception"""
    name: str = ""
    """handler name"""

    async def handle(self):
        logger.debug(f"Handle for event: {self.name}.")

        while True:
            try:
                logger.debug(f"Wait for event: {self.name}.")

                try:
                    await self.event()
                except EventCannotOccur:
                    logger.debug(f"Event never occur: {self.name}.")
                    break

                logger.debug(f"Event occurs: {self.name}.")

                logger.debug(f"Event handling: {self.name}.")

                self.handler()

                logger.debug(f"Event handled: {self.name}.")
            except Exception as ex:
                logger.error(
                    f"Event handler '{self.name}' failed.", exc_info=ex)

                if self.safe:
                    print(f"Exception in event handler {self.name}.")
                    traceback.print_exception(ex)
                else:
                    raise CoxbuildException(
                        f"Exception in event handler {self.name}", ex)

            if self.repeat == 0:
                break
            elif self.repeat > 0:
                self.repeat -= 1

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

    async def _run(self):
        logger.debug("Run service.")
        await asyncio.gather(*[e.handle() for e in self.handlers])
        logger.debug("Finish service.")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        asyncio.run(self._run())
