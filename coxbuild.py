import os
from pathlib import Path
import shutil

from coxbuild.schema import task, depend
from coxbuild.langs.python import settings
from coxbuild.langs.python.package import build as pybuild, restore as pyrestore

settings(
    requirements=Path("./requirements.txt"),
    buildSrc=Path("./src/main"),
    buildDist=Path("./selfdist")
)


@depend(pyrestore)
@task()
def build():
    readmeDst = Path("./src/main/README.md")
    shutil.copyfile(Path("README.md"), readmeDst)
    pybuild.invoke()
    os.remove(readmeDst)


@depend(build)
@task()
def default():
    pass
