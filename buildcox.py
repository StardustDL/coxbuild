import os
from pathlib import Path
import shutil

from coxbuild.schema import task, depend, setup, teardown, run
from coxbuild.extensions.python import Settings, settings as pysettings
from coxbuild.extensions.python.package import build as pybuild, restore as pyrestore, deploy as pydeploy
from coxbuild.extensions.python.format import format as pyformat

readmeDst = Path("./src/main/README.md")

pysettings(
    requirements=Path("./requirements.txt"),
    buildSrc=Path("./src/main"),
    buildDist=Path("./dist")
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


@depend(pyformat)
@task()
def format():
    pass


@task()
def install():
    run(["python", "-m", "pip", "install",
        str(list(Settings.buildDist.glob("coxbuild-*.whl"))[0])])


@depend(install)
@task()
def demo():
    run(["coxbuild", "--version"])
    run(["coxbuild", "--help"])


@depend(install)
@task()
def test_build():
    run(["coxbuild", "-vvvvv", "-D", "./test/demo"])
    res = run(["coxbuild", "-vvv", "-D", "./test/demo",
              "-f", "fail.py"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    res = run(["coxbuild", "-vvv", "-D", "./test/demo",
              "-f", "fail.py", "default2"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    run(["coxbuild", "-vvv", "-D", "./test/demo", "a"])
    run(["coxbuild", "-vvv", "-D", "./test/demo", "b"])


@depend(install)
@task()
def test_lifecycle():
    run(["coxbuild", "-vvv", "-D", "./test/demo", "-f", "lifecycle.py"])


@depend(install)
@task()
def test_command():
    run(["coxbuild", "-vvv", "-D", "./test/demo", "-f", "command.py"])
    res = run(["coxbuild", "-vvv", "-D", "./test/demo",
              "-f", "command.py", "fail", "retry"], fail=True)
    if res:
        raise Exception("Unexpected success for failing command.")


@depend(demo, test_build, test_lifecycle, test_command)
@task()
def test():
    run(["python", "-m", "pip", "uninstall",
        str(list(Settings.buildDist.glob("coxbuild-*.whl"))[0]), "-y"])


@depend(pydeploy)
@task()
def deploy():
    pass


@depend(build)
@task()
def default():
    pass
