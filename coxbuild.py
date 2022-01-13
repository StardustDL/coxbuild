import os
from pathlib import Path
import shutil

from coxbuild.schema import task, depend, before, after
from coxbuild.langs.python import settings as pysettings
from coxbuild.langs.python.package import build as pybuild, restore as pyrestore

readmeDst = Path("./src/main/README.md")

pysettings(
    requirements=Path("./requirements.txt"),
    buildSrc=Path("./src/main"),
    buildDist=Path("./selfdist")
)


@before(pybuild)
def beforeBuild():
    shutil.copyfile(Path("README.md"), readmeDst)


@after(pybuild)
def afterBuild():
    os.remove(readmeDst)


@depend(pyrestore, pybuild)
@task()
def build():
    pass


@depend(build)
@task()
def default():
    pass
