from datetime import timedelta
from pathlib import Path
from time import sleep
import os
from coxbuild.events import delay, once
from coxbuild.events.filesystems import FileSystemChangeType, FileSystemEntry, create, delete
from coxbuild.schema import on

test_file = "test/watch_temp.txt"

@on(once(create(glob=test_file, period=timedelta(seconds=0.5))))
def change(type: FileSystemChangeType, entry: FileSystemEntry):
    print(f"{type}: {entry}")


@on(once(delete(glob=test_file, period=timedelta(seconds=0.5))))
def change(type: FileSystemChangeType, entry: FileSystemEntry):
    print(f"{type}: {entry}")


@on(delay(timedelta(seconds=1)))
def createfile():
    print(f"Creating {test_file}")
    p = Path(test_file)
    p.write_text("demo text")
    print(f"Created {test_file}")


@on(delay(timedelta(seconds=2)))
def removefile():
    print(f"Removing {test_file}")
    p = Path(test_file)
    os.remove(p)
    print(f"Removed {test_file}")
