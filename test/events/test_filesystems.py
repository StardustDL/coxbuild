import asyncio
import os
from datetime import timedelta
from pathlib import Path

import pytest

from coxbuild.events import limit
from coxbuild.events.filesystems import (FileSystemChangeType, FileSystemEntry,
                                         changed)


@pytest.mark.asyncio
async def test_changed():
    file = Path("test_temp.txt")

    async def change():
        types = []
        async for context in limit(changed(glob="test_temp.txt", type={FileSystemChangeType.Create, FileSystemChangeType.Delete}, period=timedelta(seconds=0.1)), 2):
            entry: FileSystemEntry = context.kwds["entry"]
            assert entry.path.resolve() == file.resolve()
            types.append(context.kwds["type"])

        assert FileSystemChangeType.Create in types
        assert FileSystemChangeType.Delete in types

    async def touch():
        file.write_text("demo text")
        await asyncio.sleep(0.5)
        os.remove(file)

    await asyncio.gather(change(), touch())
