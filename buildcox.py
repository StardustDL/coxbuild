import os
from pathlib import Path
import shutil

from coxbuild.schema import task, depend, setup, teardown, run
from coxbuild.extensions.python import Settings, settings as pysettings
from coxbuild.extensions.python.package import build as pybuild, restore as pyrestore, deploy as pydeploy, installBuilt as install, uninstallBuilt as uninstall
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
def test_lifecycle():
    run([*demoCmdPre, "-f", "lifecycle.py"])


@depend(install)
@task()
def test_command():
    run([*demoCmdPre, "-f", "command.py"])
    res = run([*demoCmdPre,
              "-f", "command.py", "fail", "retry"], fail=True)
    if res:
        raise Exception("Unexpected success for failing command.")


@depend(demo, test_build, test_lifecycle, test_command)
@task()
def test():
    uninstall.invoke()


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
