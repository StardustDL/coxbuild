import asyncio
from datetime import datetime, time, timedelta

from coxbuild.events.datetime import attime
from coxbuild.events import once, onceevent, repeat, limit
from coxbuild.schema import on
from coxbuild.services import EventContext


@onceevent
async def e():
    await asyncio.sleep(0.5)
    print(datetime.now())


@on(repeat(e, 1))
def custom_do():
    print(f"custom done: {datetime.now()}")


next_secod = datetime.now() + timedelta(seconds=2)
print(f"schedule attimedo at {next_secod}")


@on(once(attime(next_secod)))
def attimedo():
    print(f"at time done: {datetime.now()}")


@on(repeat(e, 2, continueOnError=True), safe=True)
def unsafe_do():
    print("UNSAFE OCCUR")
    raise Exception("Unsafe op")
