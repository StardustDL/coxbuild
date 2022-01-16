from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from coxbuild import get_working_directory
from coxbuild.services import EventContext

from . import delay, occur, periodic


class FileSystemChangeType(Enum):
    Create = 0
    Modify = 1
    Access = 2
    Delete = 3


@dataclass
class FileSystemEntry:
    path: Path
    creation: datetime
    modification: datetime
    access: datetime

    def id(self):
        return str(self.path.resolve())


@dataclass
class FileEntry(FileSystemEntry):
    pass


@dataclass
class DirectoryEntry(FileSystemEntry):
    pass


class FileSystemSnapshot:
    def __init__(self,  path: Path, glob: str | None = None) -> None:
        self.entries: dict[str, FileSystemEntry] = {}
        items = path.glob(glob) if glob else [path]
        for item in items:
            item = item.resolve()
            stat = item.stat()
            ctime, mtime, atime = [datetime.fromtimestamp(
                t) for t in [stat.st_ctime, stat.st_mtime, stat.st_atime]]
            if item.is_file():
                entry = FileEntry(item, ctime, mtime, atime)
            elif item.is_dir():
                entry = DirectoryEntry(item, ctime, mtime, atime)
            if entry:
                self.entries[entry.id()] = entry


def diff(old: FileSystemSnapshot, new: FileSystemSnapshot):
    keys = set(old.entries) | set(new.entries)
    for key in keys:
        olde = old.entries.get(key)
        newe = new.entries.get(key)
        if not olde:
            yield (FileSystemChangeType.Create, newe)
        elif not newe:
            yield (FileSystemChangeType.Delete, olde)
        elif isinstance(olde, FileEntry) and isinstance(newe, FileEntry) or isinstance(olde, DirectoryEntry) and isinstance(newe, DirectoryEntry):
            if olde.creation < newe.creation:
                yield (FileSystemChangeType.Create, olde)
            if olde.modification < newe.modification:
                yield (FileSystemChangeType.Modify, olde)
            if olde.access < newe.access:
                yield (FileSystemChangeType.Access, olde)
        else:
            yield (FileSystemChangeType.Delete, olde)
            yield (FileSystemChangeType.Create, newe)


async def changed(path: Path | None = None, glob: str | None = None, type: FileSystemChangeType | None = None, period: timedelta | None = None):
    """
    Detect file or directory change (create, delete, modify, access).

    Provide event context:
        type: Type of the change, in FileSystemChangeType
        entry: Changed entry

    path: path to watch
    glob: glob pattern to watch
    type: change type to watch
    """
    period = period or timedelta(seconds=1)
    path = path or get_working_directory()

    snap = FileSystemSnapshot(path, glob)

    async for _ in periodic(period):
        newsnap = FileSystemSnapshot(path, glob)

        for ctype, entry in diff(snap, newsnap):
            if type is None or ctype == type:
                yield EventContext.build(type=ctype, entry=entry)

        snap = newsnap


def access(path: Path | None = None, glob: str | None = None, period: timedelta | None = None):
    return changed(path, glob, FileSystemChangeType.Access, period)


def create(path: Path | None = None, glob: str | None = None, period: timedelta | None = None):
    return changed(path, glob, FileSystemChangeType.Create, period)


def modify(path: Path | None = None, glob: str | None = None, period: timedelta | None = None):
    return changed(path, glob, FileSystemChangeType.Modify, period)


def delete(path: Path | None = None, glob: str | None = None, period: timedelta | None = None):
    return changed(path, glob, FileSystemChangeType.Delete, period)
