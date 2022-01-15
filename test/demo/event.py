import asyncio
from datetime import datetime

from coxbuild.schema import on


async def e():
    print(datetime.now())
    await asyncio.sleep(1)


@on(e, repeat=1)
def do():
    print(datetime.now())
    print("done")
