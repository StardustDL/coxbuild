import asyncio
from datetime import datetime, time, timedelta

from coxbuild.events import atdatetime
from coxbuild.schema import on


async def e():
    print(datetime.now())
    await asyncio.sleep(0.5)


@on(e, repeat=1)
def custom_do():
    print(f"custom done: {datetime.now()}")


next_secod = datetime.now() + timedelta(seconds=1)
print(f"schedule attimedo at {next_secod}")


@on(atdatetime(next_secod))
def attimedo():
    print(f"at time done: {datetime.now()}")


@on(e, repeat=1, safe=True)
def unsafe_do():
    raise Exception("Unsafe op")
