from pathlib import Path

import coxbuild
from coxbuild.schema import config, group, run

task = group("git")
mconfig = config.section("git")


class Repository:
    def __init__(self, root: Path) -> None:
        self.root = root

    def latestCommit(self) -> str:
        return run(["git", "rev-parse", "HEAD"], cwd=self.root).stdout.strip()

    def currentBranch(self) -> str:
        return run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.root).stdout.strip()
