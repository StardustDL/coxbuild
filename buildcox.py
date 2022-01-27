import os
import shutil
from datetime import timedelta
from pathlib import Path

import coxbuild.extensions.python.docs
import coxbuild.extensions.python.format
import coxbuild.extensions.python.package
import coxbuild.extensions.python.test
from coxbuild.extensions import projectSettings
from coxbuild.extensions.python import settings
from coxbuild.extensions.python.docs import apidoc as pyapidoc
from coxbuild.extensions.python.format import format as pyformat
from coxbuild.extensions.python.package import build as pybuild
from coxbuild.extensions.python.package import deploy as pydeploy
from coxbuild.extensions.python.package import installBuilt as install
from coxbuild.extensions.python.package import restore as pyrestore
from coxbuild.extensions.python.package import uninstallBuilt as uninstall
from coxbuild.extensions.python.test import test as pytest
from coxbuild.schema import depend, loadext, run, setup, task, teardown

loadext(coxbuild.extensions.python.docs)
loadext(coxbuild.extensions.python.format)
loadext(coxbuild.extensions.python.package)
loadext(coxbuild.extensions.python.test)

readmeDst = Path("./src/README.md")

projectSettings.docs = Path("./docs/gen/ref")


@pybuild.setup
def setupBuild():
    shutil.copyfile(Path("README.md"), readmeDst)


@pybuild.teardown
def teardownBuild():
    os.remove(readmeDst)


@depend(install)
@task
def demo():
    run(["coxbuild", "--version"])
    run(["coxbuild", "--help"])


demoCmdPre = ["coxbuild", "-vvv", "-D", "./demo"]


@depend(install)
@task
def test_build():
    run(["coxbuild", "-vvvvv", "-D", "./demo"])
    res = run([*demoCmdPre, "-f", "fail.py"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    res = run([*demoCmdPre, "-f", "fail.py", "default2"], fail=True)
    if res:
        raise Exception("Unexpected success for failing build.")
    run([*demoCmdPre, "a"])
    run([*demoCmdPre, "b"])


@depend(install)
@task
def test_builtin():
    run([*demoCmdPre, ":list"])
    run([*demoCmdPre, ":serve"])


@depend(install)
@task
def test_lifecycle():
    run([*demoCmdPre, "-f", "lifecycle.py"])


@depend(install)
@task
def test_service():
    run([*demoCmdPre, "-f", "event.py", ":serve"])


@depend(install)
@task
def test_event_fs():
    run([*demoCmdPre, "-f", "filewatch.py", ":serve"],
        timeout=timedelta(seconds=3))


@depend(install)
@task
def test_command():
    run([*demoCmdPre, "-f", "command.py"])
    res = run([*demoCmdPre,
              "-f", "command.py", "fail", "retry"], fail=True)
    if res:
        raise Exception("Unexpected success for failing command.")


@depend(test_build, test_lifecycle, test_command, test_service, test_builtin, test_event_fs)
@task
def integrationtest(): pass


@depend(pytest)
@task
def unittest(): pass


@depend(demo, integrationtest, unittest)
@task
async def test():
    await uninstall()


@depend(pyapidoc)
@task
def docs(): pass


@depend(pydeploy)
@task
def deploy(): pass


@depend(pyrestore, pybuild)
@task
def build(): pass


@depend(pyformat)
@task
def format(): pass


@depend(build)
@task
def default(): pass


@task
def serdoc():
    run(["docsify", "serve", "docs"], shell=True, fail=True)
