from coxbuild.events.datetime import attime, weekdays

import asyncio
from datetime import datetime, timedelta
from coxbuild.events import limit, once
from coxbuild.events.filesystems import FileSystemChangeType, FileSystemEntry, changed
import pytest
import os
from pathlib import Path


@pytest.mark.asyncio
async def test_attime():
    c = 0
    async for _ in attime(datetime.now() + timedelta(seconds=0.2)):
        assert c == 0
        c = 1
    assert c == 1


@pytest.mark.asyncio
async def test_weekday():
    c = 0
    async for _ in once(weekdays(datetime.today().weekday())):
        assert c == 0
        c = 1
    assert c == 1
