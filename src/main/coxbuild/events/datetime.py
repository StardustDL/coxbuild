from datetime import date, datetime, time, timedelta

from ..exceptions import EventNeverOccur
from . import delay, event


@event
async def attime(dt: datetime | date | time):
    now = datetime.now()
    now.microsecond = 0

    if isinstance(dt, date):
        dt = datetime(dt.year, dt.month, dt.day)
    elif isinstance(dt, time):
        dt = datetime(now.year, now.month, now.day,
                      dt.hour, dt.minute, dt.second)
        if dt < now:
            dt = dt + timedelta(days=1)

    if dt == now:
        return
    elif now < dt:
        await delay(dt - now)()
    else:
        raise EventNeverOccur()


@event
async def tomorrow():
    await attime(date.today() + timedelta(days=1))


@event
async def nextWeek():
    await attime(date.today() + timedelta(days=7))


@event
async def nextWeekdays(*weekdays: int):
    today = date.today()
    cur = today.weekday()
    for i in range(1, 8):
        if (cur + i) % 7 in weekdays:
            await attime(today+timedelta(days=i))
            return
    raise EventNeverOccur()


@event
async def weekdays(*weekdays: int):
    today = date.today()
    if today.weekday() in weekdays:
        return
    else:
        await nextWeekdays(weekdays)


monday = weekdays(0)
tuesday = weekdays(1)
wednesday = weekdays(2)
thursday = weekdays(3)
friday = weekdays(4)
saturday = weekdays(5)
sunday = weekdays(6)

nextMonday = nextWeekdays(0)
nextTuesday = nextWeekdays(1)
nextWednesday = nextWeekdays(2)
nextThursday = nextWeekdays(3)
nextFriday = nextWeekdays(4)
nextSaturday = nextWeekdays(5)
nextSunday = nextWeekdays(6)

weekday = weekdays(0, 1, 2, 3, 4)
weekend = weekdays(5, 6)

nextWeekday = nextWeekdays(0, 1, 2, 3, 4)
nextWeekend = nextWeekdays(5, 6)
