import asyncio
from datetime import datetime, time, timedelta

from coxbuild.events import limit, once, onceevent, repeat
from coxbuild.events.datetime import attime
from coxbuild.extensions.builtin import serve
from coxbuild.schema import after, on
from coxbuild.services import EventContext

custom_do_cnt = 0
custom_do_expect = 3

attime_do_cnt = 0
attime_do_expect = 1

unsafe_do_cnt = 0
unsafe_do_expect = 2


@onceevent
async def e():
    await asyncio.sleep(0.5)
    print(datetime.now())


@on(repeat(e, custom_do_expect-1))
def custom_do():
    global custom_do_cnt
    custom_do_cnt += 1
    print(f"custom done: {datetime.now()}")


next_secod = datetime.now() + timedelta(seconds=2)
print(f"schedule attimedo at {next_secod}")


@on(once(attime(next_secod)))
def attime_do():
    global attime_do_cnt
    attime_do_cnt += 1
    print(f"at time done: {datetime.now()}")


@on(repeat(e, unsafe_do_expect-1, continueOnError=True), safe=True)
def unsafe_do():
    global unsafe_do_cnt
    unsafe_do_cnt += 1
    print("UNSAFE OCCUR")
    raise Exception("Unsafe op")


@after(serve)
def check(context, result):
    assert attime_do_cnt == attime_do_expect
    assert custom_do_cnt == custom_do_expect
    assert unsafe_do_cnt == unsafe_do_expect
    print("Passed post-check.")
