from datetime import date, datetime, time, timedelta

from . import delay, limit, occur, once, onceevent


async def attime(dt: datetime | date | time):
    while True:
        now = datetime.now()

        if isinstance(dt, datetime):
            cdt = dt
        elif isinstance(dt, date):
            cdt = datetime(dt.year, dt.month, dt.day,
                           now.hour, now.minute, now.second)
        elif isinstance(dt, time):
            cdt = datetime(now.year, now.month, now.day,
                           dt.hour, dt.minute, dt.second)
            if cdt < now:
                cdt = cdt + timedelta(days=1)

        if cdt.date() == now.date() and cdt.hour == now.hour and cdt.minute == now.minute and cdt.second == now.second:
            yield
        elif now < cdt:
            await occur(delay(cdt - now))
            yield
        else:
            break

        print(dt, cdt, datetime.now())

        # go to next time span

        if isinstance(dt, time):
            await occur(delay(timedelta(hours=1)))
        elif isinstance(dt, datetime):
            await occur(delay(timedelta(seconds=1)))


def tomorrow():
    return attime(date.today() + timedelta(days=1))


def nextWeek():
    return attime(date.today() + timedelta(days=7))


async def weekdays(*weekdays: int):
    while True:
        today = date.today()
        cur = today.weekday()
        if cur in weekdays:
            yield
        else:
            done = False
            for i in range(1, 8):
                if (cur + i) % 7 in weekdays:
                    done = True
                    await occur(attime(today+timedelta(days=i)))
                    yield
                    await occur(tomorrow())
            if not done:
                break

monday = weekdays(0)
tuesday = weekdays(1)
wednesday = weekdays(2)
thursday = weekdays(3)
friday = weekdays(4)
saturday = weekdays(5)
sunday = weekdays(6)

weekday = weekdays(0, 1, 2, 3, 4)
weekend = weekdays(5, 6)
