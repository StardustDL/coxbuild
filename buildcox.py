import os
import shutil
from datetime import timedelta
from pathlib import Path

from coxbuild.extensions.python.all import Settings
from coxbuild.extensions.python.all import build as pybuild
from coxbuild.extensions.python.all import deploy as pydeploy
from coxbuild.extensions.python.all import format as pyformat
from coxbuild.extensions.python.all import installBuilt as install
from coxbuild.extensions.python.all import restore as pyrestore
from coxbuild.extensions.python.all import settings as pysettings
from coxbuild.extensions.python.all import uninstallBuilt as uninstall
from coxbuild.extensions.python.all import test as pytest
from coxbuild.schema import depend, run, setup, task, teardown

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


@depend(install)
@task()
def demo():
    run(["coxbuild", "--version"])
    run(["coxbuild", "--help"])


demoCmdPre = ["coxbuild", "-vvv", "-D", "./test/demo"]


@depend(install)
@task()
def test_build():
    run(["coxbuild", "-vvvvv", "-D", "./test/demo"])
    res = run([*demoCmdPre, "-f", "fail.py"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    res = run([*demoCmdPre, "-f", "fail.py", "default2"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    run([*demoCmdPre, "a"])
    run([*demoCmdPre, "b"])


@depend(install)
@task()
def test_builtin():
    run([*demoCmdPre, ":list"])
    run([*demoCmdPre, ":serve"])


@depend(install)
@task()
def test_lifecycle():
    run([*demoCmdPre, "-f", "lifecycle.py"])


@depend(install)
@task()
def test_service():
    run([*demoCmdPre, "-f", "event.py", ":serve"])


@depend(install)
@task()
def test_event_fs():
    run([*demoCmdPre, "-f", "filewatch.py", ":serve"],
        timeout=timedelta(seconds=3))


@depend(install)
@task()
def test_command():
    run([*demoCmdPre, "-f", "command.py"])
    res = run([*demoCmdPre,
              "-f", "command.py", "fail", "retry"], fail=True)
    if res:
        raise Exception("Unexpected success for failing command.")


@depend(demo, test_build, test_lifecycle, test_command, test_service, test_builtin, test_event_fs, pytest)
@task()
def test():
    uninstall()


@depend(pydeploy)
@task()
def deploy():
    pass


@depend(pyrestore, pybuild)
@task()
def build():
    pass


@depend(pyformat)
@task()
def format():
    pass


@depend(build)
@task()
def default():
    pass
