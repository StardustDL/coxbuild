import os
from pathlib import Path
import shutil

from coxbuild.schema import task, depend, setup, teardown
from coxbuild.langs.python import settings as pysettings
from coxbuild.langs.python.package import build as pybuild, restore as pyrestore

readmeDst = Path("./src/main/README.md")

pysettings(
    requirements=Path("./requirements.txt"),
    buildSrc=Path("./src/main"),
    buildDist=Path("./selfdist")
)


@setup(pybuild)
def setupBuild():
    shutil.copyfile(Path("README.md"), readmeDst)


@teardown(pybuild)
def teardownBuild():
    os.remove(readmeDst)


@depend(pyrestore, pybuild)
@task()
def build():
    pass


@depend(build)
@task()
def default():
    pass
